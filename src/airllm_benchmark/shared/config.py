"""Configuration loader for AirLLM Benchmark.

Re-exports from config_models and config_loader for backward compatibility.
All logic flows through separated modules.
"""

from airllm_benchmark.shared.config_loader import (
    get_hf_token,
    load_experiment,
    load_hardware,
    validate_hardware,
)
from airllm_benchmark.shared.config_models import (
    CONFIG_DIR,
    REQUIRED_EXPERIMENT_KEYS,
    ExperimentConfig,
    HardwareConfig,
)

__all__ = [
    "CONFIG_DIR",
    "ExperimentConfig",
    "HardwareConfig",
    "REQUIRED_EXPERIMENT_KEYS",
    "get_hf_token",
    "load_experiment",
    "load_hardware",
    "validate_hardware",
]
