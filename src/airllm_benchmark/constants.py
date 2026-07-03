"""Enums and physical constants for the benchmark.

Contains immutable values used across the project:
- Benchmark modes (GPU provider, CPU baseline, AirLLM)
- Run status values (success, OOM, timeout)
- Quantization levels
"""

from enum import StrEnum


class BenchmarkMode(StrEnum):
    """Benchmark inference modes."""

    GPU_PROVIDER = "gpu_provider"
    CPU_BASELINE = "cpu_baseline"
    AIRLLM = "airllm"


class RunStatus(StrEnum):
    """Possible outcomes of a benchmark run."""

    SUCCESS = "success"
    OOM = "oom"
    TIMEOUT = "timeout"


class QuantizationLevel(StrEnum):
    """Supported quantization levels for AirLLM."""

    NONE = "none"
    Q4 = "4bit"
    Q8 = "8bit"


# Physical constants
MEMORY_SAMPLE_INTERVAL = 1.0  # seconds between psutil memory samples
