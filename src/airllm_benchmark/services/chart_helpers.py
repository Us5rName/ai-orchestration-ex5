"""Matplotlib rendering helpers for Visualizer.

Extracted from pocs/visualization_pipeline_poc.py (task 4.3).
Adapted to work with real MetricsRecord instead of fake data.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from .metrics import MetricsRecord

# Color palette for consistent chart styling across modes.
_MODE_COLORS: list[str] = ["#2196F3", "#F44336", "#4CAF50"]


def _render_bar_chart(
    labels: list[str],
    values: list[float],
    ylabel: str,
    title: str,
    output_path: str,
) -> str:
    """Render a bar chart and save as PNG.

    Args:
        labels: X-axis category labels (e.g. mode names).
        values: Y-axis numeric values.
        ylabel: Label for the Y-axis.
        title: Chart title.
        output_path: File path for the output PNG.

    Returns:
        Absolute path to the generated PNG file.
    """
    colors = _MODE_COLORS[: len(values)]
    # Cycle colors if more bars than palette entries.
    while len(colors) < len(values):
        colors.extend(_MODE_COLORS[: len(values) - len(colors)])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_ylim(0, max(values) * 1.15 if values else 1.0)

    fig.tight_layout()
    fig.savefig(output_path, dpi=100)
    plt.close(fig)

    return os.path.abspath(output_path)


def render_latency_chart(
    records: list[MetricsRecord],
    output_path: str,
) -> str:
    """Generate a bar chart comparing total_runtime_s across modes.

    Reuses proven pattern from pocs/visualization_pipeline_poc.py.

    Args:
        records: Metrics records to visualise.
        output_path: Destination file path.

    Returns:
        Absolute path to the generated PNG.
    """
    modes = [r.mode for r in records]
    runtimes = [r.total_runtime_s for r in records]

    return _render_bar_chart(
        labels=modes,
        values=runtimes,
        ylabel="Total Runtime (seconds)",
        title="Inference Latency Comparison",
        output_path=output_path,
    )


def render_memory_chart(
    records: list[MetricsRecord],
    output_path: str,
) -> str:
    """Generate a bar chart comparing peak_ram_mb across modes.

    Reuses proven pattern from pocs/visualization_pipeline_poc.py.

    Args:
        records: Metrics records to visualise.
        output_path: Destination file path.

    Returns:
        Absolute path to the generated PNG.
    """
    modes = [r.mode for r in records]
    ram_values = [r.peak_ram_mb for r in records]

    return _render_bar_chart(
        labels=modes,
        values=ram_values,
        ylabel="Peak RAM (MB)",
        title="Memory Usage Comparison",
        output_path=output_path,
    )
