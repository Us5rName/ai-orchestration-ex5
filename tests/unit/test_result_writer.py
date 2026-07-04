"""Unit tests for ResultWriter — JSON persistence of MetricsRecord.

Tests exercise append, load, and clear against a temporary file path.
All file I/O is real (no mocking) since ResultWriter is a thin
persistence layer with no external network dependencies.

Run:
    uv run pytest tests/unit/test_result_writer.py -v
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from airllm_benchmark.services.metrics_helpers import MetricsRecord
from airllm_benchmark.services.result_writer import ResultWriter


@pytest.fixture
def tmp_json(tmp_path: Path) -> str:
    """Return a unique JSON file path inside the temp directory."""
    return str(tmp_path / "metrics.json")


@pytest.fixture
def writer(tmp_json: str) -> ResultWriter:
    """Return a ResultWriter targeting a temp file."""
    return ResultWriter(tmp_json)


@pytest.fixture
def sample_record() -> MetricsRecord:
    """Deterministic MetricsRecord for tests."""
    return MetricsRecord(
        run_id="run_001",
        model="test/model",
        mode="cpu_baseline",
        provider="transformers",
        prompt="Hello",
        prompt_id="P1",
        quantization="none",
        max_new_tokens=32,
        load_time_s=1.5,
        ttft_s=0.5,
        total_runtime_s=2.0,
        tokens_generated=20,
        generation_throughput=10.0,
        peak_ram_mb=500.0,
        peak_vram_mb=0.0,
        status="success",
        error="",
        timestamp="2024-01-01T00:00:00+00:00",
    )


class TestAppend:
    """Tests for ResultWriter.append()."""

    def test_creates_file(self, writer: ResultWriter, sample_record: MetricsRecord) -> None:
        writer.append(sample_record)
        assert os.path.exists(writer._path)

    def test_creates_parent_dirs(self, tmp_path: Path, sample_record: MetricsRecord) -> None:
        """Append creates nested parent directories."""
        nested = str(tmp_path / "a" / "b" / "c" / "metrics.json")
        ResultWriter(nested).append(sample_record)
        assert os.path.exists(nested)

    def test_appends_cumulative(self, writer: ResultWriter, sample_record: MetricsRecord) -> None:
        writer.append(sample_record)
        writer.append(sample_record)
        with open(writer._path) as f:
            data = json.load(f)
        assert len(data) == 2

    def test_round_trip_values(self, writer: ResultWriter, sample_record: MetricsRecord) -> None:
        writer.append(sample_record)
        with open(writer._path) as f:
            data = json.load(f)
        assert data[0]["run_id"] == "run_001"
        assert data[0]["model"] == "test/model"
        assert data[0]["peak_ram_mb"] == 500.0


class TestLoad:
    """Tests for ResultWriter.load()."""

    def test_empty_when_missing(self, writer: ResultWriter) -> None:
        assert writer.load() == []

    def test_returns_records(self, writer: ResultWriter, sample_record: MetricsRecord) -> None:
        writer.append(sample_record)
        records = writer.load()
        assert len(records) == 1
        assert isinstance(records[0], MetricsRecord)

    def test_multiple_records(self, writer: ResultWriter, sample_record: MetricsRecord) -> None:
        writer.append(sample_record)
        writer.append(sample_record)
        assert len(writer.load()) == 2

    def test_empty_file(self, tmp_json: str) -> None:
        """Load from an empty JSON array file."""
        with open(tmp_json, "w") as f:
            json.dump([], f)
        assert ResultWriter(tmp_json).load() == []


class TestClear:
    """Tests for ResultWriter.clear()."""

    def test_clears_records(self, writer: ResultWriter, sample_record: MetricsRecord) -> None:
        writer.append(sample_record)
        writer.clear()
        assert writer.load() == []

    def test_noop_when_missing(self, writer: ResultWriter) -> None:
        # Should not raise even when file doesn't exist
        writer.clear()
        assert writer.load() == []

    def test_creates_file(self, writer: ResultWriter) -> None:
        writer.clear()
        assert os.path.exists(writer._path)
        with open(writer._path) as f:
            assert json.load(f) == []
