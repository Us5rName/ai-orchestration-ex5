"""V6-V7 memory/throughput scatter charts for the reporting layer (§5.2).

Split from report_charts_extra.py to stay under the 150-line limit.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import report_helpers as _helpers

if TYPE_CHECKING:
    from collections.abc import Callable

    from .metrics import MetricsRecord


def _render_scatter_by_mode(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
    output_dir: str,
    *,
    x_field: str,
    xlabel: str,
    title: str,
    output_filename: str,
) -> str:
    """Shared scatter renderer: x_field (x) vs generation_throughput (y).

    Successful runs only, colored by mode, annotated by tier. Backs both
    V6 (peak_ram_mb) and V7 (peak_vram_mb).
    """
    successful = [r for r in records if r.status == "success"]
    if not successful:
        return ""

    fig, ax = plt.subplots(figsize=(10, 6))
    seen_modes: set[str] = set()
    for r in successful:
        mode_color = _helpers.MODE_COLORS.get(r.mode, "#9E9E9E")
        label = r.mode if r.mode not in seen_modes else None
        seen_modes.add(r.mode)
        x_value = getattr(r, x_field)
        ax.scatter(x_value, r.generation_throughput, color=mode_color, s=80, label=label)
        ax.annotate(
            tier_lookup(r.model),
            (x_value, r.generation_throughput),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
        )

    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel("Throughput (tok/s)", fontsize=11)
    ax.set_title(title, fontsize=13)
    ax.tick_params(axis="both", labelsize=10)
    ax.legend(fontsize=9)

    output_path = os.path.join(output_dir, output_filename)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)


def render_memory_vs_throughput_scatter(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
    output_dir: str,
) -> str:
    """V6: scatter of peak_ram_mb (x) vs generation_throughput (y), successful runs only."""
    return _render_scatter_by_mode(
        records,
        tier_lookup,
        output_dir,
        x_field="peak_ram_mb",
        xlabel="Peak RAM (MB)",
        title="Memory vs Throughput Trade-off",
        output_filename="memory_vs_throughput.png",
    )


def render_vram_vs_throughput_scatter(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
    output_dir: str,
) -> str:
    """V7: scatter of peak_vram_mb (x) vs generation_throughput (y), successful runs only."""
    return _render_scatter_by_mode(
        records,
        tier_lookup,
        output_dir,
        x_field="peak_vram_mb",
        xlabel="Peak VRAM (MB)",
        title="VRAM vs Throughput Trade-off",
        output_filename="vram_vs_throughput.png",
    )
