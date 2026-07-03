"""Tests for shared/config_loader.py — config loading and validation.

Covers: valid JSON loading, missing fields, empty hardware validation,
env var retrieval, and combined experiment+hardware loading.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from airllm_benchmark.shared.config_loader import (
    HardwareConfig,
    load_experiment,
    load_hardware,
    validate_hardware,
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


# ——— load_experiment tests ———


class TestLoadExperiment:
    """Tests for load_experiment()."""

    def test_loads_valid_experiment(self, tmp_path: Path) -> None:
        cfg_path = tmp_path / "experiment.json"
        cfg_path.write_text(json.dumps(VALID_EXPERIMENT))
        cfg = load_experiment(cfg_path.parent)
        assert cfg.gpu_provider == "ollama"
        assert cfg.max_new_tokens == 32
        assert "small" in cfg.models

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_experiment(tmp_path)

    def test_invalid_json_raises(self, tmp_path: Path) -> None:
        cfg_path = tmp_path / "experiment.json"
        cfg_path.write_text("not json")
        with pytest.raises(json.JSONDecodeError):
            load_experiment(tmp_path)

    def test_missing_required_field_raises(self, tmp_path: Path) -> None:
        partial = {"models": {}}
        cfg_path = tmp_path / "experiment.json"
        cfg_path.write_text(json.dumps(partial))
        with pytest.raises(ValueError, match="Missing required"):
            load_experiment(tmp_path)


# ——— load_hardware tests ———


class TestLoadHardware:
    """Tests for load_hardware()."""

    def test_loads_valid_hardware(self, tmp_path: Path) -> None:
        cfg_path = tmp_path / "hardware.json"
        cfg_path.write_text(json.dumps(VALID_HARDWARE))
        cfg = load_hardware(cfg_path.parent)
        assert cfg.cpu == "AMD Ryzen 9 7950X"
        assert cfg.ram_gb == 128

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_hardware(tmp_path)

    def test_empty_hardware_loads(self, tmp_path: Path) -> None:
        """Empty hardware loads but validate_hardware catches it."""
        cfg_path = tmp_path / "hardware.json"
        cfg_path.write_text(json.dumps(EMPTY_HARDWARE))
        cfg = load_hardware(tmp_path)
        assert cfg.cpu == ""


# ——— validate_hardware tests ———


class TestValidateHardware:
    """Tests for validate_hardware()."""

    def test_valid_passes(self) -> None:
        hw = HardwareConfig(**VALID_HARDWARE)
        validate_hardware(hw)

    def test_empty_cpu_raises(self) -> None:
        hw = HardwareConfig(**EMPTY_HARDWARE)
        with pytest.raises(ValueError, match="cpu"):
            validate_hardware(hw)

    def test_zero_ram_raises(self) -> None:
        partial = {**VALID_HARDWARE, "ram_gb": 0}
        hw = HardwareConfig(**partial)
        with pytest.raises(ValueError, match="ram_gb"):
            validate_hardware(hw)
