"""Unit tests for Visualizer generate_all and VisualizationResult.

Tests the full visualization pipeline and result dataclass.
Single responsibility: aggregate pipeline + result type.

Run:
    uv run pytest tests/unit/test_visualizer_generate_all.py -v
"""

from __future__ import annotations

import dataclasses
import os
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from airllm_benchmark.services.metrics import MetricsRecord

from airllm_benchmark.services.visualizer import (
    VisualizationResult,
    Visualizer,
)


class TestVisualizerGenerateAll:
    """Test generate_all produces all charts."""

    def test_returns_two_paths(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer()
            paths = viz.generate_all(sample_records, tmpdir)
            assert len(paths) == 2

    def test_all_paths_exist(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer()
            paths = viz.generate_all(sample_records, tmpdir)
            for path in paths:
                assert os.path.isfile(path)

    def test_all_paths_absolute(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer()
            paths = viz.generate_all(sample_records, tmpdir)
            for path in paths:
                assert os.path.isabs(path)

    def test_includes_latency_and_memory(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer()
            paths = viz.generate_all(sample_records, tmpdir)
            names = [os.path.basename(p) for p in paths]
            assert "latency_chart.png" in names
            assert "memory_chart.png" in names


class TestVisualizationResult:
    """Test VisualizationResult dataclass."""

    def test_is_frozen(self) -> None:
        """Dataclass should be immutable."""
        result = VisualizationResult(
            chart_paths=["a.png", "b.png"],
            table_text="table",
        )
        try:
            result.chart_paths = ["c.png"]  # type: ignore[union-attr]
            raise AssertionError("Expected FrozenInstanceError")
        except dataclasses.FrozenInstanceError:
            pass

    def test_has_required_fields(self) -> None:
        result = VisualizationResult(
            chart_paths=["chart.png"],
            table_text="data",
        )
        assert result.chart_paths == ["chart.png"]
        assert result.table_text == "data"

    def test_multiple_chart_paths(self) -> None:
        result = VisualizationResult(
            chart_paths=["latency.png", "memory.png"],
            table_text="| A | B |",
        )
        assert len(result.chart_paths) == 2
        assert "latency.png" in result.chart_paths
