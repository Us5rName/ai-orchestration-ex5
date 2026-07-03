"""Configuration data models for AirLLM Benchmark.

Defines typed, immutable dataclasses for experiment and hardware
configuration. Separates data structure from loading logic.
"""

from __future__ import annotations

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
