"""Tests for Metrics + Visualization Pipeline PoC.

End-to-end test: collect fake metrics -> generate chart -> verify PNG output.
Per TODO.md task 4.3 Definition of Done.

Run:
    uv run pytest tests/pocs/test_visualization_pipeline_poc.py -v
"""

from __future__ import annotations

import os
import tempfile

from pocs.visualization_pipeline_poc import (
    generate_fake_records,
    generate_latency_bar_chart,
    generate_memory_bar_chart,
    run_pipeline,
)


class TestPoCFakeRecords:
    """Verify fake metrics records are generated correctly."""

    def test_returns_three_records(self) -> None:
        records = generate_fake_records()
        assert len(records) == 3

    def test_all_modes_present(self) -> None:
        records = generate_fake_records()
        modes = {r.mode for r in records}
        assert modes == {"gpu_provider", "cpu_baseline", "airllm"}

    def test_runtime_values_positive(self) -> None:
        records = generate_fake_records()
        for r in records:
            assert r.total_runtime_s > 0

    def test_memory_values_positive(self) -> None:
        records = generate_fake_records()
        for r in records:
            assert r.peak_ram_mb > 0


class TestPoCLatencyChart:
    """Verify latency chart generation produces valid PNG."""

    def test_chart_file_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "latency.png")
            result = generate_latency_bar_chart(generate_fake_records(), out_path)
            assert os.path.isfile(result)

    def test_chart_is_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "latency.png")
            result = generate_latency_bar_chart(generate_fake_records(), out_path)
            assert result.endswith(".png")

    def test_chart_has_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "latency.png")
            result = generate_latency_bar_chart(generate_fake_records(), out_path)
            size = os.path.getsize(result)
            assert size > 0

    def test_chart_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "latency.png")
            result = generate_latency_bar_chart(generate_fake_records(), out_path)
            assert os.path.isabs(result)


class TestPoCMemoryChart:
    """Verify memory chart generation produces valid PNG."""

    def test_chart_file_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "memory.png")
            result = generate_memory_bar_chart(generate_fake_records(), out_path)
            assert os.path.isfile(result)

    def test_chart_has_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "memory.png")
            result = generate_memory_bar_chart(generate_fake_records(), out_path)
            size = os.path.getsize(result)
            assert size > 0


class TestPoCFullPipeline:
    """End-to-end: fake metrics -> charts -> verify PNG output."""

    def test_pipeline_returns_both_charts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_pipeline(tmpdir)
            assert "latency" in result
            assert "memory" in result

    def test_pipeline_creates_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "nested", "charts")
            result = run_pipeline(nested)
            assert os.path.isdir(nested)
            assert len(result) == 2

    def test_pipeline_files_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_pipeline(tmpdir)
            for path in result.values():
                assert os.path.isfile(path)

    def test_pipeline_files_have_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_pipeline(tmpdir)
            for path in result.values():
                assert os.path.getsize(path) > 0

    def test_pipeline_output_paths_absolute(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_pipeline(tmpdir)
            for path in result.values():
                assert os.path.isabs(path)
