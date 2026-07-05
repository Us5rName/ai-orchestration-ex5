"""Shared 300-DPI grouped/stacked bar chart renderer for the report layer.

New, additive module — does not modify chart_helpers.py. Used by
report_charts.py to render V1-V4 (grouped/stacked bars).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from matplotlib.axes import Axes

_OOM_HATCH = "//"
_BAR_WIDTH = 0.8


def _apply_report_style(ax: Axes, ylabel: str, title: str) -> None:
    """Apply shared font/label styling used across all report charts."""
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=13)
    ax.tick_params(axis="both", labelsize=10)


def render_grouped_bar_chart(
    groups: list[str],
    series: dict[str, list[tuple[float, bool]]],
    colors: dict[str, str],
    ylabel: str,
    title: str,
    output_path: str,
    *,
    value_labels: bool = True,
    oom_hatch: bool = True,
    reference_line: tuple[float, str] | None = None,
) -> str:
    """Render a grouped bar chart (one bar per series within each group).

    Args:
        groups: X-axis group labels (e.g. tier names), in display order.
        series: Series name -> list of (value, is_success) pairs, one per
            group, aligned with `groups`. Bars where is_success is False
            are hatched (if oom_hatch) to flag OOM/timeout/error runs.
        colors: Series name -> hex color.
        ylabel: Y-axis label.
        title: Chart title.
        output_path: Destination PNG path.
        value_labels: Whether to draw value labels above each bar.
        oom_hatch: Whether to hatch bars flagged as non-success.
        reference_line: Optional (y_value, label) horizontal reference line.

    Returns:
        Absolute path to the generated PNG file.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    n_series = len(series)
    n_groups = len(groups)
    group_positions = range(n_groups)
    bar_width = _BAR_WIDTH / max(n_series, 1)

    for i, (name, values) in enumerate(series.items()):
        offsets = [pos + (i - (n_series - 1) / 2) * bar_width for pos in group_positions]
        heights = [v for v, _ in values]
        bars = ax.bar(
            offsets,
            heights,
            width=bar_width,
            label=name,
            color=colors.get(name, "#9E9E9E"),
        )
        for bar, (value, is_success) in zip(bars, values, strict=True):
            if oom_hatch and not is_success:
                bar.set_hatch(_OOM_HATCH)
                bar.set_edgecolor("black")
            if value_labels and value > 0:
                ax.annotate(
                    f"{value:.1f}",
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    textcoords="offset points",
                    xytext=(0, 3),
                    ha="center",
                    fontsize=9,
                )

    if reference_line is not None:
        y_value, label = reference_line
        ax.axhline(y_value, color="black", linestyle="--", linewidth=1.5)
        ax.annotate(label, (0, y_value), textcoords="offset points", xytext=(0, 5), fontsize=9)

    ax.set_xticks(list(group_positions))
    ax.set_xticklabels(groups, fontsize=10)
    ax.legend(fontsize=9)
    _apply_report_style(ax, ylabel, title)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    return os.path.abspath(output_path)


def render_stacked_bar_chart(
    groups: list[str],
    segments: dict[str, list[float]],
    colors: dict[str, str],
    ylabel: str,
    title: str,
    output_path: str,
) -> str:
    """Render a stacked bar chart (segments stacked within each group bar).

    Args:
        groups: X-axis group labels, in display order.
        segments: Segment name -> list of values (one per group, aligned
            with `groups`), stacked bottom-to-top in dict iteration order.
        colors: Segment name -> hex color.
        ylabel: Y-axis label.
        title: Chart title.
        output_path: Destination PNG path.

    Returns:
        Absolute path to the generated PNG file.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    bottoms = [0.0] * len(groups)
    for name, values in segments.items():
        ax.bar(groups, values, bottom=bottoms, label=name, color=colors.get(name, "#9E9E9E"))
        bottoms = [b + v for b, v in zip(bottoms, values, strict=True)]

    ax.legend(fontsize=9)
    _apply_report_style(ax, ylabel, title)
    ax.tick_params(axis="x", labelsize=10)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    return os.path.abspath(output_path)
