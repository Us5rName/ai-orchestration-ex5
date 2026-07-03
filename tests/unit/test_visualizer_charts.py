"""Unit tests for Visualizer chart generation.

Tests latency and memory bar charts produce valid PNG output.
Single responsibility: chart rendering only.

Run:
    uv run pytest tests/unit/test_visualizer_charts.py -v
"""

from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from airllm_benchmark.services.metrics import MetricsRecord

from airllm_benchmark.services.visualizer import Visualizer


class TestVisualizerLatencyChart:
    """Test generate_latency_chart produces valid PNG output."""

    def test_returns_absolute_path(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer()
            path = viz.generate_latency_chart(sample_records, tmpdir)
            assert os.path.isabs(path)

    def test_file_exists(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer()
            path = viz.generate_latency_chart(sample_records, tmpdir)
            assert os.path.isfile(path)

    def test_creates_output_directory(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "charts", "nested")
            viz = Visualizer()
            path = viz.generate_latency_chart(sample_records, nested)
            assert os.path.isfile(path)
            assert os.path.isdir(nested)

    def test_file_is_png(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer()
            path = viz.generate_latency_chart(sample_records, tmpdir)
            assert path.endswith(".png")

    def test_file_has_content(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer()
            path = viz.generate_latency_chart(sample_records, tmpdir)
            assert os.path.getsize(path) > 0


class TestVisualizerMemoryChart:
    """Test generate_memory_chart produces valid PNG output."""

    def test_returns_absolute_path(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer()
            path = viz.generate_memory_chart(sample_records, tmpdir)
            assert os.path.isabs(path)

    def test_file_exists(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer()
            path = viz.generate_memory_chart(sample_records, tmpdir)
            assert os.path.isfile(path)

    def test_file_has_content(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer()
            path = viz.generate_memory_chart(sample_records, tmpdir)
            assert os.path.getsize(path) > 0
