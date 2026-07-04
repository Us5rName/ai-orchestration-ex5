"""ResultWriter Feature PoCs — Prove append, load, and clear with real MetricsRecord.

Each PoC isolates a single interface method and exercises it against
the actual filesystem with a real MetricsRecord instance.

Run:
    uv run python pocs/result_writer_feature_poc.py
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from airllm_benchmark.services.metrics_helpers import MetricsRecord

_POC_FILE = "results/poc_feature_test.json"


def poc_append(record: MetricsRecord, path: str) -> None:
    """Append one MetricsRecord to a JSON array file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict] = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = json.load(f)
    existing.append(asdict(record))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


def poc_load(path: str) -> list[MetricsRecord]:
    """Load all persisted MetricsRecords from a JSON array file."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [MetricsRecord(**item) for item in raw]


def poc_clear(path: str) -> None:
    """Replace the JSON file with an empty array."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([], f)


def _make_record(idx: int) -> MetricsRecord:
    """Create a deterministic MetricsRecord for PoC testing."""
    return MetricsRecord(
        run_id=f"poc_run_{idx:03d}",
        model=f"test/model_{idx}",
        mode="cpu_baseline",
        provider="transformers",
        prompt=f"Prompt {idx}",
        prompt_id=f"P{idx}",
        quantization="none",
        max_new_tokens=32,
        load_time_s=float(idx) * 0.5,
        ttft_s=float(idx) * 0.1,
        total_runtime_s=float(idx) * 1.2,
        tokens_generated=idx * 10,
        generation_throughput=float(idx) * 5.0,
        peak_ram_mb=float(idx) * 100.0,
        peak_vram_mb=0.0,
        status="success",
        error="",
        timestamp=f"2024-01-01T00:00:{idx:02d}+00:00",
    )


if __name__ == "__main__":
    if os.path.exists(_POC_FILE):
        os.remove(_POC_FILE)

    r1 = _make_record(1)
    poc_append(r1, _POC_FILE)
    assert os.path.exists(_POC_FILE), "File should exist after append"
    print("append PoC: file created")

    r2 = _make_record(2)
    poc_append(r2, _POC_FILE)
    with open(_POC_FILE) as f:
        data = json.load(f)
    assert len(data) == 2, "Should have 2 records after two appends"
    print("append PoC: cumulative append OK")

    records = poc_load(_POC_FILE)
    assert len(records) == 2, "Load should return 2 records"
    assert isinstance(records[0], MetricsRecord)
    assert records[0].run_id == "poc_run_001"
    print("load PoC: round-trip OK")

    empty = poc_load("results/nonexistent.json")
    assert empty == [], "Load missing file should return []"
    print("load PoC: missing file OK")

    poc_clear(_POC_FILE)
    cleared = poc_load(_POC_FILE)
    assert cleared == [], "Clear should result in empty list"
    print("clear PoC: OK")

    os.remove(_POC_FILE)
    print("\nAll Feature PoCs: PASSED")
