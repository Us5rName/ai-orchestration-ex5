"""MetricsRecord + config fixtures for the reporting-layer tests.

Provides records covering multiple tiers, an OOM status, and
distinct prompt_ids (P1-P3) — separate from fixtures_metrics.py,
which stays untouched per the additive-only constraint.
"""

from __future__ import annotations

import pytest

from airllm_benchmark.services.metrics import MetricsRecord
from airllm_benchmark.shared.config_models import ExperimentConfig


def _record(**overrides: object) -> MetricsRecord:
    base: dict[str, object] = {
        "run_id": "run_000",
        "model": "test/small",
        "mode": "gpu_provider",
        "provider": "transformers",
        "prompt": "Hello",
        "prompt_id": "P1",
        "quantization": "none",
        "max_new_tokens": 32,
        "load_time_s": 0.5,
        "ttft_s": 0.6,
        "total_runtime_s": 1.2,
        "tokens_generated": 20,
        "generation_throughput": 20.0,
        "peak_ram_mb": 450.0,
        "peak_vram_mb": 200.0,
        "status": "success",
        "error": "",
        "timestamp": "2024-01-01T00:00:00+00:00",
    }
    base.update(overrides)
    return MetricsRecord(**base)


@pytest.fixture
def sample_report_records() -> list[MetricsRecord]:
    """Records spanning small/medium/large tiers, all three modes, an
    OOM failure, and distinct prompt_ids (P1-P3) for V5 sensitivity."""
    return [
        _record(run_id="run_001", model="test/small", mode="gpu_provider", prompt_id="P1"),
        _record(
            run_id="run_002",
            model="test/small",
            mode="cpu_baseline",
            prompt_id="P2",
            total_runtime_s=2.0,
            peak_ram_mb=500.0,
        ),
        _record(
            run_id="run_003",
            model="test/medium",
            mode="airllm",
            prompt_id="P3",
            total_runtime_s=8.0,
            load_time_s=2.0,
            ttft_s=2.5,
            peak_ram_mb=1200.0,
            peak_vram_mb=0.0,
        ),
        _record(
            run_id="run_004",
            model="test/large",
            mode="cpu_baseline",
            prompt_id="P1",
            status="oom",
            error="CUDA out of memory",
            total_runtime_s=0.0,
            generation_throughput=0.0,
            peak_ram_mb=62000.0,
            peak_vram_mb=0.0,
            tokens_generated=0,
        ),
        _record(
            run_id="run_005",
            model="test/large",
            mode="airllm",
            prompt_id="P2",
            total_runtime_s=45.0,
            load_time_s=5.0,
            ttft_s=6.0,
            peak_ram_mb=8000.0,
            peak_vram_mb=0.0,
            generation_throughput=5.0,
        ),
    ]


@pytest.fixture
def empty_prompt_id_records() -> list[MetricsRecord]:
    """Records where every prompt_id is empty — V5 must skip gracefully."""
    return [
        _record(run_id="run_010", prompt_id=""),
        _record(run_id="run_011", mode="cpu_baseline", prompt_id=""),
    ]


@pytest.fixture
def report_experiment() -> ExperimentConfig:
    """Minimal ExperimentConfig mapping test model ids to tiers."""
    return ExperimentConfig(
        models={
            "small": {"id": "test/small", "tier": "small"},
            "medium": {"id": "test/medium", "tier": "medium"},
            "large": {"id": "test/large", "tier": "large"},
        },
        prompts={"P1": "a", "P2": "b", "P3": "c"},
        max_new_tokens=32,
        quantization="none",
        gpu_provider="transformers",
        cpu_baseline_provider="transformers",
        provider_config={},
    )
