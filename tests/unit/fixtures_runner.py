"""Shared fixtures for runner unit tests.

Provides mock providers and MetricsCollector patches used across
all runner test modules to avoid duplication.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from airllm_benchmark.services.metrics import MetricsRecord


@pytest.fixture
def mock_provider() -> MagicMock:
    """Mock InferenceProvider with default success behavior."""
    provider = MagicMock()
    provider.generate.return_value = ("generated output", 15)
    return provider


def _make_gpu_record(
    status: str = "success",
    error: str = "",
    tokens: int = 15,
) -> MetricsRecord:
    """Create a GPU MetricsRecord for fixture use."""
    return MetricsRecord(
        run_id="r1",
        model="m",
        mode="gpu_provider",
        provider="p",
        prompt="x",
        prompt_id="P1",
        quantization="none",
        max_new_tokens=32,
        load_time_s=0.5,
        ttft_s=0.5,
        total_runtime_s=1.0,
        tokens_generated=tokens,
        generation_throughput=float(tokens),
        peak_ram_mb=100.0,
        peak_vram_mb=50.0,
        status=status,
        error=error,
        timestamp="2024-01-01T00:00:00+00:00",
    )


def _make_cpu_record(
    status: str = "success",
    error: str = "",
    tokens: int = 15,
) -> MetricsRecord:
    """Create a CPU MetricsRecord for fixture use."""
    return MetricsRecord(
        run_id="r1",
        model="m",
        mode="cpu_baseline",
        provider="p",
        prompt="x",
        prompt_id="P1",
        quantization="none",
        max_new_tokens=32,
        load_time_s=0.5,
        ttft_s=0.5,
        total_runtime_s=1.0,
        tokens_generated=tokens,
        generation_throughput=float(tokens),
        peak_ram_mb=100.0,
        peak_vram_mb=0.0,
        status=status,
        error=error,
        timestamp="2024-01-01T00:00:00+00:00",
    )


def _make_airllm_record(
    status: str = "success",
    error: str = "",
    tokens: int = 15,
    quantization: str = "4bit",
) -> MetricsRecord:
    """Create an AirLLM MetricsRecord for fixture use."""
    return MetricsRecord(
        run_id="r1",
        model="m",
        mode="airllm",
        provider="airllm",
        prompt="x",
        prompt_id="P1",
        quantization=quantization,
        max_new_tokens=32,
        load_time_s=0.5,
        ttft_s=0.5,
        total_runtime_s=1.0,
        tokens_generated=tokens,
        generation_throughput=float(tokens),
        peak_ram_mb=100.0,
        peak_vram_mb=0.0,
        status=status,
        error=error,
        timestamp="2024-01-01T00:00:00+00:00",
    )
