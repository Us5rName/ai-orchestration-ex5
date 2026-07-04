"""Feature PoC for AirLLM metrics collection — real MetricsCollector lifecycle.

Proves that MetricsCollector can track timing and RAM during a real
AirLLM inference run. Exercises the full lifecycle: start, load,
generation, stop, and record assembly.

Per docs/IMPLEMENTATION.md Step 2 — Feature PoCs.
Always test against real data.

    uv run pytest tests/pocs/test_airllm_metrics_poc.py -v -s
"""

from __future__ import annotations

import pytest

from tests.pocs._cuda import has_cuda


@pytest.mark.skipif(not has_cuda(), reason="CUDA not available — PoC requires GPU hardware")
def test_collector_lifecycle_produces_valid_record() -> None:
    """MetricsCollector records timing and RAM from a real AirLLM run."""
    from airllm_benchmark.sdk.airllm_generator import generate_text
    from airllm_benchmark.sdk.airllm_loader import load_model
    from airllm_benchmark.services.metrics import MetricsCollector

    collector = MetricsCollector(sampling_interval=0.5)
    collector.start(
        model_id="Qwen/Qwen2.5-0.5B-Instruct",
        mode="airllm",
        provider="airllm",
        prompt="What is 1+1?",
        prompt_id="P1",
        quantization="4bit",
        max_tokens=8,
    )

    model = load_model("Qwen/Qwen2.5-0.5B-Instruct", "4bit")
    collector.mark_load_complete()

    collector.mark_generation_start()
    output, tokens = generate_text(model, "What is 1+1?", 8)
    collector.stop()

    record = collector.get_record(
        tokens_generated=tokens,
        status="success",
        error="",
    )

    # Verify all required fields
    assert record.status == "success"
    assert record.model == "Qwen/Qwen2.5-0.5B-Instruct"
    assert record.mode == "airllm"
    assert record.provider == "airllm"
    assert record.quantization == "4bit"
    assert record.max_new_tokens == 8
    assert record.tokens_generated > 0
    assert record.load_time_s > 0, "Load time must be positive"
    assert record.ttft_s > 0, "TTFT must be positive"
    assert record.total_runtime_s > 0, "Total runtime must be positive"
    assert record.peak_ram_mb > 0, "RAM must be measurable"
    assert record.generation_throughput > 0, "Throughput must be positive"

    print("\n===== Metrics Collection PoC =====")
    print(f"Load time:      {record.load_time_s:.2f}s")
    print(f"TTFT:           {record.ttft_s:.2f}s")
    print(f"Total runtime:  {record.total_runtime_s:.2f}s")
    print(f"Tokens gen:     {record.tokens_generated}")
    print(f"Throughput:     {record.generation_throughput:.2f} tok/s")
    print(f"Peak RAM:       {record.peak_ram_mb:.1f} MB")
    print(f"Peak VRAM:      {record.peak_vram_mb:.1f} MB")
    print(f"Status:         {record.status}")
    print("==================================\n")
