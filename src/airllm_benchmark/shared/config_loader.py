"""Configuration loading and validation for AirLLM Benchmark.

Handles file I/O, JSON parsing, and field validation for config files.
Separates loading logic from data model definitions.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from airllm_benchmark.shared.config_models import (
    CONFIG_DIR,
    REQUIRED_EXPERIMENT_KEYS,
    ExperimentConfig,
    HardwareConfig,
)


def _parse_config(path: Path) -> dict:
    """Read and parse a JSON config file."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path) as f:
        return json.load(f)


def load_experiment(config_dir: Path | None = None) -> ExperimentConfig:
    """Load experiment configuration from config/experiment.json.

    Args:
        config_dir: Optional directory override (defaults to project config/).

    Returns:
        ExperimentConfig with all experiment parameters.

    Raises:
        FileNotFoundError: If experiment.json is missing.
        ValueError: If required fields are absent.
    """
    base = config_dir or CONFIG_DIR
    data = _parse_config(base / "experiment.json")
    missing = REQUIRED_EXPERIMENT_KEYS - set(data.keys())
    if missing:
        raise ValueError(f"Missing required keys: {', '.join(sorted(missing))}")
    return ExperimentConfig(**data)


def load_hardware(config_dir: Path | None = None) -> HardwareConfig:
    """Load hardware configuration from config/hardware.json.

    Args:
        config_dir: Optional directory override (defaults to project config/).

    Returns:
        HardwareConfig with documented hardware specs.

    Raises:
        FileNotFoundError: If hardware.json is missing.
    """
    base = config_dir or CONFIG_DIR
    data = _parse_config(base / "hardware.json")
    return HardwareConfig(**data)


def validate_hardware(hw: HardwareConfig) -> None:
    """Validate that all hardware fields are filled.

    Args:
        hw: HardwareConfig to validate.

    Raises:
        ValueError: If any required field is empty or zero.
    """
    if not hw.cpu:
        raise ValueError("Hardware field 'cpu' must be filled")
    if not hw.gpu:
        raise ValueError("Hardware field 'gpu' must be filled")
    if hw.ram_gb <= 0:
        raise ValueError("Hardware field 'ram_gb' must be > 0")
    if hw.vram_gb <= 0:
        raise ValueError("Hardware field 'vram_gb' must be > 0")
    if hw.disk_free_gb <= 0:
        raise ValueError("Hardware field 'disk_free_gb' must be > 0")
    if not hw.os:
        raise ValueError("Hardware field 'os' must be filled")
    if not hw.documented_by:
        raise ValueError("Hardware field 'documented_by' must be filled")
    if not hw.documented_at:
        raise ValueError("Hardware field 'documented_at' must be filled")


def validate_config(config_dir: Path | None = None) -> None:
    """Validate that both experiment and hardware configs are loadable.

    Args:
        config_dir: Optional directory override.

    Raises:
        FileNotFoundError: If either config file is missing.
        ValueError: If required fields are absent or hardware fields are empty.
    """
    load_experiment(config_dir)
    hw = load_hardware(config_dir)
    validate_hardware(hw)


def get_hf_token() -> str | None:
    """Get HuggingFace token from environment variables.

    Returns:
        HF_TOKEN value or None if not set.
    """
    return os.environ.get("HF_TOKEN")
