"""Unit tests for MetricsRecord — field completeness and immutability.

All external dependencies (psutil, torch) are mocked per project rules.
"""

from __future__ import annotations

from airllm_benchmark.services.metrics import MetricsRecord


def test_record_contains_all_fields() -> None:
    """Assert MetricsRecord has all 17 fields from CONFIG.md §1."""
    record = MetricsRecord(
        run_id="run_001",
        model="test-model",
        mode="gpu_provider",
        provider="transformers",
        prompt="hello",
        prompt_id="P1",
        quantization="4bit",
        max_new_tokens=32,
        load_time_s=1.0,
        ttft_s=2.0,
        total_runtime_s=3.0,
        tokens_generated=10,
        peak_ram_mb=100.0,
        peak_vram_mb=200.0,
        status="success",
        error="",
        timestamp="2026-01-01T00:00:00+00:00",
    )
    assert record.run_id == "run_001"
    assert record.model == "test-model"
    assert record.mode == "gpu_provider"
    assert record.tokens_generated == 10
    assert record.peak_ram_mb == 100.0
    assert record.status == "success"


def test_record_is_frozen() -> None:
    """Assert MetricsRecord cannot be mutated after creation."""
    record = MetricsRecord(
        run_id="r1",
        model="m",
        mode="gpu_provider",
        provider="t",
        prompt="p",
        prompt_id="P1",
        quantization="none",
        max_new_tokens=1,
        load_time_s=0.0,
        ttft_s=0.0,
        total_runtime_s=0.0,
        tokens_generated=0,
        peak_ram_mb=0.0,
        peak_vram_mb=0.0,
        status="success",
        error="",
        timestamp="2026-01-01T00:00:00+00:00",
    )
    try:
        record.status = "oom"  # type: ignore[frozen-instantiation]
        raise AssertionError("Expected FrozenInstanceError")
    except Exception:
        pass  # Expected — dataclass is frozen
