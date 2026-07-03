"""Tests for shared/config_models.py — configuration dataclasses.

Covers: ExperimentConfig accessors, HardwareConfig completeness check,
and edge cases for missing keys.
"""

from __future__ import annotations

import pytest

from airllm_benchmark.shared.config_models import (
    ExperimentConfig,
    HardwareConfig,
)

VALID_EXPERIMENT = {
    "models": {
        "small": {"id": "meta-llama/Llama-3.2-1B", "tier": "small"},
    },
    "prompts": {"P1": "What is the capital?"},
    "max_new_tokens": 32,
    "quantization": "4bit",
    "gpu_provider": "ollama",
    "cpu_baseline_provider": "transformers",
    "provider_config": {
        "ollama": {"base_url": "http://localhost:11434"},
    },
}

VALID_HARDWARE = {
    "cpu": "AMD Ryzen 9 7950X",
    "gpu": "NVIDIA RTX 4090 24GB",
    "ram_gb": 128,
    "disk_free_gb": 500,
    "os": "Ubuntu 24.04",
    "documented_by": "tester",
    "documented_at": "2026-07-03T00:00:00",
}

EMPTY_HARDWARE = {
    "cpu": "",
    "gpu": "",
    "ram_gb": 0,
    "disk_free_gb": 0,
    "os": "",
    "documented_by": "",
    "documented_at": "",
}


# ——— ExperimentConfig tests ———


class TestExperimentConfig:
    """Tests for ExperimentConfig dataclass."""

    def test_get_model_id(self) -> None:
        cfg = ExperimentConfig(**VALID_EXPERIMENT)
        assert cfg.get_model_id("small") == "meta-llama/Llama-3.2-1B"

    def test_get_model_id_missing_raises(self) -> None:
        cfg = ExperimentConfig(**VALID_EXPERIMENT)
        with pytest.raises(KeyError):
            cfg.get_model_id("nonexistent")

    def test_get_prompt(self) -> None:
        cfg = ExperimentConfig(**VALID_EXPERIMENT)
        assert cfg.get_prompt("P1") == "What is the capital?"


# ——— HardwareConfig tests ———


class TestHardwareConfig:
    """Tests for HardwareConfig dataclass."""

    def test_is_complete_true(self) -> None:
        hw = HardwareConfig(**VALID_HARDWARE)
        assert hw.is_complete() is True

    def test_is_complete_false(self) -> None:
        hw = HardwareConfig(**EMPTY_HARDWARE)
        assert hw.is_complete() is False
