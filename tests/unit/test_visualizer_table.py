"""Unit tests for Visualizer table generation.

Tests formatted comparison table output.
Single responsibility: table formatting only.

Run:
    uv run pytest tests/unit/test_visualizer_table.py -v
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from airllm_benchmark.services.metrics import MetricsRecord

from airllm_benchmark.services.visualizer import Visualizer


class TestVisualizerTable:
    """Test generate_table produces formatted text."""

    def test_returns_string(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        viz = Visualizer()
        table = viz.generate_table(sample_records)
        assert isinstance(table, str)

    def test_contains_mode_names(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        viz = Visualizer()
        table = viz.generate_table(sample_records)
        assert "gpu_provider" in table
        assert "cpu_baseline" in table
        assert "airllm" in table

    def test_contains_header(
        self,
        sample_records: list[MetricsRecord],
    ) -> None:
        viz = Visualizer()
        table = viz.generate_table(sample_records)
        assert "Mode" in table
        assert "Runtime" in table

    def test_empty_records_returns_message(self) -> None:
        viz = Visualizer()
        table = viz.generate_table([])
        assert "No records" in table
