"""Tests for sdk/sdk_validation.py — pre-benchmark validation (task 7.4).

Verifies config/provider/cache checks without touching real config
files, real providers, or the real HF cache. All external calls
(config loading, provider construction, cache scan) are mocked.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.sdk.sdk_validation import ValidationResult, run_validation

_MOD = "airllm_benchmark.sdk.sdk_validation"


class TestValidationResult:
    """Tests for the ValidationResult dataclass."""

    def test_passed_true_when_config_ok_and_providers_ok(self) -> None:
        """passed is True when config is valid and all providers constructed."""
        result = ValidationResult(config_ok=True, config_error="", providers={"transformers": True})
        assert result.passed is True

    def test_passed_false_when_config_invalid(self) -> None:
        """passed is False when config failed to load/validate."""
        result = ValidationResult(config_ok=False, config_error="boom")
        assert result.passed is False

    def test_passed_false_when_a_provider_failed(self) -> None:
        """passed is False if any provider failed to construct."""
        result = ValidationResult(
            config_ok=True, config_error="", providers={"transformers": False}
        )
        assert result.passed is False

    def test_passed_ignores_model_cache_status(self) -> None:
        """Missing cache entries do not fail validation (informational only)."""
        result = ValidationResult(
            config_ok=True,
            config_error="",
            providers={"transformers": True},
            models_cached={"org/model": False},
        )
        assert result.passed is True


class TestRunValidation:
    """Tests for run_validation()."""

    def test_config_failure_short_circuits(self) -> None:
        """A config load/validate failure skips provider and cache checks."""
        with patch(f"{_MOD}.load_experiment", side_effect=FileNotFoundError("missing")):
            result = run_validation()

        assert result.config_ok is False
        assert "missing" in result.config_error
        assert result.providers == {}
        assert result.models_cached == {}

    def test_hardware_validation_failure_reported(self) -> None:
        """A hardware validation ValueError is captured, not raised."""
        with (
            patch(f"{_MOD}.load_experiment"),
            patch(f"{_MOD}.load_hardware"),
            patch(f"{_MOD}.validate_hardware", side_effect=ValueError("cpu missing")),
        ):
            result = run_validation()

        assert result.config_ok is False
        assert "cpu missing" in result.config_error

    def test_success_path_reports_providers_and_cache(self, mock_config: MagicMock) -> None:
        """A fully valid config reports provider success and cache status."""
        with (
            patch(f"{_MOD}.load_experiment", return_value=mock_config),
            patch(f"{_MOD}.load_hardware"),
            patch(f"{_MOD}.validate_hardware"),
            patch(f"{_MOD}._helpers.create_provider", return_value=MagicMock()),
            patch(f"{_MOD}.model_cache_status", return_value={"test/small": True}),
        ):
            result = run_validation()

        assert result.config_ok is True
        assert result.providers == {"transformers": True}
        assert result.models_cached == {"test/small": True}
        assert result.passed is True

    def test_provider_construction_failure_reported_per_provider(
        self, mock_config: MagicMock
    ) -> None:
        """A provider construction failure is captured with its error message."""
        mock_config.gpu_provider = "ollama"
        mock_config.cpu_baseline_provider = "transformers"
        with (
            patch(f"{_MOD}.load_experiment", return_value=mock_config),
            patch(f"{_MOD}.load_hardware"),
            patch(f"{_MOD}.validate_hardware"),
            patch(
                f"{_MOD}._helpers.create_provider",
                side_effect=ValueError("Unsupported provider: 'ollama'"),
            ),
            patch(f"{_MOD}.model_cache_status", return_value={}),
        ):
            result = run_validation()

        assert result.config_ok is True
        assert result.providers["ollama"] is False
        assert "Unsupported provider" in result.provider_errors["ollama"]
        assert result.passed is False
