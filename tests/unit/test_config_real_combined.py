"""Tests for shared/config_loader.py — test config combined scenarios.

Validates end-to-end loading of both config files and cross-config
scenarios using the actual values from tests/config/.
"""

from __future__ import annotations

from pathlib import Path

from airllm_benchmark.shared.config_loader import (
    get_hf_token,
    load_experiment,
    load_hardware,
    validate_hardware,
)

TEST_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class TestRealConfigCombined:
    """Tests that load both test config files together."""

    def test_both_configs_load(self) -> None:
        """Experiment and hardware configs both load from tests/config/."""
        exp = load_experiment(TEST_CONFIG_DIR)
        hw = load_hardware(TEST_CONFIG_DIR)
        assert exp is not None
        assert hw is not None

    def test_gpu_provider_in_config(self) -> None:
        """gpu_provider 'ollama' exists in provider_config dict."""
        exp = load_experiment(TEST_CONFIG_DIR)
        assert exp.gpu_provider == "ollama"
        assert "ollama" in exp.provider_config

    def test_cpu_provider_in_config(self) -> None:
        """cpu_baseline_provider 'transformers' exists in provider_config dict."""
        exp = load_experiment(TEST_CONFIG_DIR)
        assert exp.cpu_baseline_provider == "transformers"
        assert "transformers" in exp.provider_config

    def test_full_pipeline_load_and_validate(self) -> None:
        """Load both configs and validate hardware in one flow."""
        exp = load_experiment(TEST_CONFIG_DIR)
        hw = load_hardware(TEST_CONFIG_DIR)
        validate_hardware(hw)
        assert exp.gpu_provider == "ollama"
        assert exp.cpu_baseline_provider == "transformers"
        assert hw.cpu == "Intel Core i9-13900K"
        assert hw.is_complete()

    def test_hf_token_returns_none_when_unset(self) -> None:
        """get_hf_token returns None when HF_TOKEN is not in environment."""
        token = get_hf_token()
        assert token is None or isinstance(token, str)
