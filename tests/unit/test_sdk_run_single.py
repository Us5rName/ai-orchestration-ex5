"""BenchmarkSDK.run_single() tests.

Verifies single-run dispatch: runner selection, provider creation,
quantization passthrough, and custom provider override.

Per docs/TODO.md task 5.7 — split by interface method.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.metrics import MetricsRecord


@pytest.fixture
def _record() -> MetricsRecord:
    """Deterministic MetricsRecord for run_single assertions."""
    return MetricsRecord(
        run_id="r1",
        model="m",
        mode="gpu_provider",
        provider="t",
        prompt="p",
        prompt_id="P1",
        quantization="none",
        max_new_tokens=32,
        load_time_s=1.0,
        ttft_s=1.0,
        total_runtime_s=2.0,
        tokens_generated=10,
        generation_throughput=10.0,
        peak_ram_mb=100.0,
        peak_vram_mb=50.0,
        status="success",
        error="",
        timestamp="2024-01-01T00:00:00+00:00",
    )


class TestRunSingle:
    """BenchmarkSDK.run_single() tests."""

    def test_dispatches_correct_runner(
        self, mock_config: MagicMock, _record: MetricsRecord
    ) -> None:
        """run_single dispatches to the correct runner for mode."""
        mock_runner = MagicMock()
        mock_runner.run.return_value = _record
        mock_provider = MagicMock()

        with (
            patch("airllm_benchmark.sdk.sdk.load_experiment", return_value=mock_config),
            patch(
                "airllm_benchmark.sdk.sdk._helpers.create_provider",
                return_value=mock_provider,
            ),
        ):
            sdk = BenchmarkSDK()
            sdk._runner_mgr = MagicMock()
            sdk._runner_mgr.get_runner.return_value = mock_runner

            result = sdk.run_single(
                model_id="test/small",
                mode="gpu_provider",
                prompt="Hello",
            )

            assert result is _record
            mock_runner.run.assert_called_once()

    def test_custom_provider_override(self, mock_config: MagicMock, _record: MetricsRecord) -> None:
        """run_single uses custom provider when provided."""
        mock_runner = MagicMock()
        mock_runner.run.return_value = _record
        mock_provider = MagicMock()

        with (
            patch("airllm_benchmark.sdk.sdk.load_experiment", return_value=mock_config),
            patch(
                "airllm_benchmark.sdk.sdk._helpers.create_provider",
                return_value=mock_provider,
            ) as mock_create,
        ):
            sdk = BenchmarkSDK()
            sdk._runner_mgr = MagicMock()
            sdk._runner_mgr.get_runner.return_value = mock_runner

            sdk.run_single(
                model_id="test/small",
                mode="gpu_provider",
                prompt="Hello",
                provider="custom_provider",
            )

            mock_create.assert_called_with("custom_provider", mock_config.provider_config)

    def test_quantization_passed_through(
        self, mock_config: MagicMock, _record: MetricsRecord
    ) -> None:
        """run_single passes quantization to runner."""
        mock_runner = MagicMock()
        mock_runner.run.return_value = _record
        mock_provider = MagicMock()

        with (
            patch("airllm_benchmark.sdk.sdk.load_experiment", return_value=mock_config),
            patch(
                "airllm_benchmark.sdk.sdk._helpers.create_provider",
                return_value=mock_provider,
            ),
        ):
            sdk = BenchmarkSDK()
            sdk._runner_mgr = MagicMock()
            sdk._runner_mgr.get_runner.return_value = mock_runner

            sdk.run_single(
                model_id="test/small",
                mode="gpu_provider",
                prompt="Hello",
                quantization="4bit",
            )

            call_kwargs = mock_runner.run.call_args.kwargs
            assert call_kwargs["quantization"] == "4bit"
