"""ResultWriter Real-Data PoC — Persist and load real MetricsRecord instances.

Exercises the full ResultWriter module against the actual filesystem
with MetricsRecord instances matching CONFIG.md §1 schema.  This PoC
proves the module works end-to-end before it is consumed by the SDK.

Run:
    uv run python pocs/result_writer_real_data_poc.py
"""

from __future__ import annotations

import json
import os

from airllm_benchmark.services.metrics_helpers import MetricsRecord
from airllm_benchmark.services.result_writer import ResultWriter

_OUTPUT = "results/real_data_poc.json"


def _make_records() -> list[MetricsRecord]:
    """Create realistic MetricsRecord instances for PoC testing."""
    return [
        MetricsRecord(
            run_id="run_001",
            model="Qwen/Qwen2.5-0.5B-Instruct",
            mode="gpu_provider",
            provider="transformers",
            prompt="What is the capital of France?",
            prompt_id="P1",
            quantization="none",
            max_new_tokens=32,
            load_time_s=1.2,
            ttft_s=0.3,
            total_runtime_s=1.8,
            tokens_generated=28,
            generation_throughput=15.0,
            peak_ram_mb=800.0,
            peak_vram_mb=600.0,
            status="success",
            error="",
            timestamp="2024-07-04T10:00:00+00:00",
        ),
        MetricsRecord(
            run_id="run_002",
            model="Qwen/Qwen2.5-0.5B-Instruct",
            mode="cpu_baseline",
            provider="transformers",
            prompt="What is the capital of France?",
            prompt_id="P1",
            quantization="none",
            max_new_tokens=32,
            load_time_s=3.5,
            ttft_s=1.2,
            total_runtime_s=5.1,
            tokens_generated=28,
            generation_throughput=8.5,
            peak_ram_mb=1200.0,
            peak_vram_mb=0.0,
            status="success",
            error="",
            timestamp="2024-07-04T10:05:00+00:00",
        ),
        MetricsRecord(
            run_id="run_003",
            model="Qwen/Qwen2.5-0.5B-Instruct",
            mode="airllm",
            provider="airllm",
            prompt="What is the capital of France?",
            prompt_id="P1",
            quantization="4bit",
            max_new_tokens=32,
            load_time_s=2.0,
            ttft_s=0.8,
            total_runtime_s=3.2,
            tokens_generated=28,
            generation_throughput=10.5,
            peak_ram_mb=600.0,
            peak_vram_mb=0.0,
            status="success",
            error="",
            timestamp="2024-07-04T10:10:00+00:00",
        ),
    ]


def main() -> None:
    """Run the real-data PoC."""
    writer = ResultWriter(_OUTPUT)

    # Clean previous run
    writer.clear()

    # Append records individually (as Runner Manager would do)
    records = _make_records()
    for rec in records:
        writer.append(rec)
        print(f"  Appended: {rec.run_id} ({rec.mode})")

    # Load and verify round-trip
    loaded = writer.load()
    print(f"\nLoaded {len(loaded)} records from {_OUTPUT}")

    for rec in loaded:
        print(
            f"  {rec.run_id}: {rec.model} | {rec.mode} | "
            f"runtime={rec.total_runtime_s}s | ram={rec.peak_ram_mb}MB | "
            f"status={rec.status}"
        )

    # Verify raw JSON structure
    with open(_OUTPUT, encoding="utf-8") as f:
        raw = json.load(f)
    print(f"\nJSON array has {len(raw)} entries")
    print(f"First record keys: {sorted(raw[0].keys())}")

    # Verify schema matches CONFIG.md §1
    expected_keys = {
        "run_id",
        "model",
        "mode",
        "provider",
        "prompt",
        "prompt_id",
        "quantization",
        "max_new_tokens",
        "load_time_s",
        "ttft_s",
        "total_runtime_s",
        "tokens_generated",
        "generation_throughput",
        "peak_ram_mb",
        "peak_vram_mb",
        "status",
        "error",
        "timestamp",
    }
    assert set(raw[0].keys()) == expected_keys, "Schema mismatch"
    print("Schema matches CONFIG.md §1: OK")

    # Cleanup
    os.remove(_OUTPUT)
    print(f"\nCleaned up {_OUTPUT}")
    print("Real-Data PoC: PASSED")


if __name__ == "__main__":
    main()
