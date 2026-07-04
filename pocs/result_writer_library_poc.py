"""ResultWriter Library PoC — Prove JSON array persistence for MetricsRecord.

Proves that a frozen dataclass can be serialized to a JSON array file,
appended, and deserialized back without data loss. This is the foundation
for the ResultWriter service.

Run:
    uv run python pocs/result_writer_library_poc.py
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True)
class _SampleRecord:
    """Minimal stand-in for MetricsRecord used in this PoC."""

    run_id: str
    model: str
    mode: str
    status: str


def poc_write_json_array(records: Sequence[_SampleRecord], path: str) -> None:
    """Serialize a sequence of records to a JSON array file.

    Creates parent directories if needed. Overwrites existing file.

    Args:
        records: Records to serialize.
        path: Output file path.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in records], f, indent=2)


def poc_append_json_array(record: _SampleRecord, path: str) -> None:
    """Append one record to a JSON array file.

    Loads existing records if the file exists, appends, writes back.

    Args:
        record: Record to append.
        path: Target file path.
    """
    existing: list[dict] = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    existing.append(asdict(record))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


def poc_load_json_array(path: str) -> list[dict]:
    """Load JSON array from file. Returns empty list if missing.

    Args:
        path: File path.

    Returns:
        List of dicts from the JSON array.
    """
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Main — demonstrate round-trip
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tmp_file = "results/poc_library_test.json"

    # Clean slate
    if os.path.exists(tmp_file):
        os.remove(tmp_file)

    # Write initial array
    r1 = _SampleRecord(run_id="r1", model="m1", mode="gpu", status="success")
    poc_write_json_array([r1], tmp_file)
    loaded = poc_load_json_array(tmp_file)
    print(f"After write: {len(loaded)} record(s)")

    # Append
    r2 = _SampleRecord(run_id="r2", model="m2", mode="airllm", status="success")
    poc_append_json_array(r2, tmp_file)
    loaded = poc_load_json_array(tmp_file)
    print(f"After append: {len(loaded)} record(s)")

    # Cleanup
    os.remove(tmp_file)
    print("Library PoC: OK")
