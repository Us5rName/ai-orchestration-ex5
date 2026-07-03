"""Configuration loader for AirLLM Benchmark.

Loads experiment.json, hardware.json, and .env values.
Returns typed config objects. Aborts on empty hardware fields.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "config"

REQUIRED_EXPERIMENT_KEYS = {
    "models",
    "prompts",
    "max_new_tokens",
    "quantization",
    "gpu_provider",
    "cpu_baseline_provider",
    "provider_config",
}


@dataclass(frozen=True)
class ExperimentConfig:
    """Typed configuration from config/experiment.json.

    Input:  Parsed JSON dict with experiment parameters.
    Output: Immutable config with model/prompt accessors.
    Setup:  Loaded via load_experiment().
    """

    models: dict[str, dict[str, str]]
    prompts: dict[str, str]
    max_new_tokens: int
    quantization: str
    gpu_provider: str
    cpu_baseline_provider: str
    provider_config: dict[str, Any]

    def get_model_id(self, name: str) -> str:
        """Return the HuggingFace model ID for the given tier name."""
        return self.models[name]["id"]

    def get_prompt(self, prompt_id: str) -> str:
        """Return the prompt text for the given prompt ID."""
        return self.prompts[prompt_id]


@dataclass(frozen=True)
class HardwareConfig:
    """Typed configuration from config/hardware.json.

    Input:  Parsed JSON dict with hardware specs.
    Output: Immutable config with completeness check.
    Setup:  Loaded via load_hardware().
    """

    cpu: str
    gpu: str
    ram_gb: float
    disk_free_gb: float
    os: str
    documented_by: str
    documented_at: str

    def is_complete(self) -> bool:
        """Return True if all hardware fields are filled."""
        return bool(
            self.cpu
            and self.gpu
            and self.ram_gb > 0
            and self.disk_free_gb > 0
            and self.os
            and self.documented_by
            and self.documented_at
        )


def _parse_config(path: Path) -> dict[str, Any]:
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
    if hw.disk_free_gb <= 0:
        raise ValueError("Hardware field 'disk_free_gb' must be > 0")
    if not hw.os:
        raise ValueError("Hardware field 'os' must be filled")
    if not hw.documented_by:
        raise ValueError("Hardware field 'documented_by' must be filled")
    if not hw.documented_at:
        raise ValueError("Hardware field 'documented_at' must be filled")


def get_hf_token() -> str | None:
    """Get HuggingFace token from environment variables.

    Returns:
        HF_TOKEN value or None if not set.
    """
    return os.environ.get("HF_TOKEN")
