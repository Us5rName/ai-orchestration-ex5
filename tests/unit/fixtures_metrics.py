"""Sample MetricsRecord fixtures for visualizer tests.

Provides deterministic MetricsRecord instances covering all
inference modes (GPU, CPU, AirLLM) to avoid circular dependencies.
"""

from __future__ import annotations

import pytest

from airllm_benchmark.services.metrics import MetricsRecord


@pytest.fixture
def sample_records() -> list[MetricsRecord]:
    """Deterministic MetricsRecord instances for visualizer tests.

    Three records covering all inference modes: GPU, CPU, AirLLM.
    """
    return [
        MetricsRecord(
            run_id="run_001",
            model="test/small",
            mode="gpu_provider",
            provider="ollama",
            prompt="Hello",
            prompt_id="P1",
            quantization="none",
            max_new_tokens=32,
            load_time_s=0.5,
            ttft_s=0.5,
            total_runtime_s=1.2,
            tokens_generated=20,
            generation_throughput=20.0,
            peak_ram_mb=450.0,
            peak_vram_mb=200.0,
            status="success",
            error="",
            timestamp="2024-01-01T00:00:00+00:00",
        ),
        MetricsRecord(
            run_id="run_002",
            model="test/large",
            mode="cpu_baseline",
            provider="transformers",
            prompt="Hello",
            prompt_id="P1",
            quantization="none",
            max_new_tokens=32,
            load_time_s=10.0,
            ttft_s=10.0,
            total_runtime_s=45.0,
            tokens_generated=20,
            generation_throughput=20.0,
            peak_ram_mb=1800.0,
            peak_vram_mb=0.0,
            status="success",
            error="",
            timestamp="2024-01-01T00:01:00+00:00",
        ),
        MetricsRecord(
            run_id="run_003",
            model="test/large",
            mode="airllm",
            provider="airllm",
            prompt="Hello",
            prompt_id="P1",
            quantization="4bit",
            max_new_tokens=32,
            load_time_s=3.0,
            ttft_s=3.0,
            total_runtime_s=12.5,
            tokens_generated=20,
            generation_throughput=20.0,
            peak_ram_mb=900.0,
            peak_vram_mb=0.0,
            status="success",
            error="",
            timestamp="2024-01-01T00:02:00+00:00",
        ),
    ]
