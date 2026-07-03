"""Visualization service for inference benchmark metrics.

Generates bar charts (latency, memory) and comparison tables from
MetricsRecord data. All chart output is saved as PNG to `assets/`.

Per INTERFACES.md §6-§7 and PLAN C3 chart_generator + table_generator.
Built from proven PoC code (pocs/visualization_pipeline_poc.py, task 4.3).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from . import chart_helpers as _charts
from . import table_helpers as _tables
from .metrics import MetricsRecord

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class VisualizationResult:
    """Result from visualization generation.

    Returned by BenchmarkSDK.generate_visualization().
    Per INTERFACES.md §7.
    """

    chart_paths: list[str]
    table_text: str


class Visualizer:
    """Generates charts and tables from inference benchmark metrics.

    Delegates rendering to chart_helpers and table_helpers to stay
    within the 150-line file limit while keeping single responsibility.

    Input:
        records: List of MetricsRecord instances.
        output_dir: Directory for PNG output (default: "assets").

    Output:
        Chart file paths (str), formatted table text (str),
        or VisualizationResult with both.
    """

    def generate_latency_chart(
        self,
        records: list[MetricsRecord],
        output_dir: str = "assets",
    ) -> str:
        """Generate a bar chart comparing total_runtime_s across modes.

        Args:
            records: List of metrics records to visualize.
            output_dir: Directory to save the chart PNG.

        Returns:
            File path to the generated chart.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = os.path.join(output_dir, "latency_chart.png")
        return _charts.render_latency_chart(records, output_path)

    def generate_memory_chart(
        self,
        records: list[MetricsRecord],
        output_dir: str = "assets",
    ) -> str:
        """Generate a bar chart comparing peak_ram_mb across modes.

        Args:
            records: List of metrics records to visualize.
            output_dir: Directory to save the chart PNG.

        Returns:
            File path to the generated chart.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = os.path.join(output_dir, "memory_chart.png")
        return _charts.render_memory_chart(records, output_path)

    def generate_table(self, records: list[MetricsRecord]) -> str:
        """Generate a formatted comparison table from metrics records.

        Args:
            records: List of metrics records to tabulate.

        Returns:
            Formatted table string suitable for printing or saving.
        """
        return _tables.format_comparison_table(records)

    def generate_all(
        self,
        records: list[MetricsRecord],
        output_dir: str = "assets",
    ) -> list[str]:
        """Generate all charts and return their file paths.

        Args:
            records: List of metrics records to visualize.
            output_dir: Directory to save chart PNGs.

        Returns:
            List of file paths to all generated PNG assets.
        """
        latency_path = self.generate_latency_chart(records, output_dir)
        memory_path = self.generate_memory_chart(records, output_dir)
        return [latency_path, memory_path]
