"""V1-V3 comparison charts for the reporting layer (§5.2).

New, additive module. V4-V6 live in report_charts_extra.py to keep
both files under the 150-line limit.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from . import report_chart_core as _core
from . import report_helpers as _helpers

if TYPE_CHECKING:
    from collections.abc import Callable

    from .metrics import MetricsRecord


def _grouped_series(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
    value_field: str,
    *,
    successful_only: bool = False,
) -> tuple[list[str], dict[str, list[tuple[float, bool]]]]:
    """Shape records into (tier groups, series-by-mode) for a grouped chart.

    Missing (tier, mode) combinations are filled with a zero-value,
    successful placeholder so every series has one entry per group.
    """
    if successful_only:
        records = [r for r in records if r.status == "success"]

    groups = _helpers.group_by_tier_and_mode(records, tier_lookup)
    tiers = sorted({tier for tier, _ in groups}, key=_helpers.tier_sort_key)
    modes = sorted({mode for _, mode in groups})

    series: dict[str, list[tuple[float, bool]]] = {mode: [] for mode in modes}
    for tier in tiers:
        for mode in modes:
            recs = groups.get((tier, mode), [])
            if not recs:
                series[mode].append((0.0, True))
                continue
            value = sum(getattr(r, value_field) for r in recs) / len(recs)
            is_success = all(r.status == "success" for r in recs)
            series[mode].append((value, is_success))

    return tiers, series


def render_latency_by_tier_chart(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
    output_dir: str,
) -> str:
    """V1: grouped bar chart of total_runtime_s by tier x mode."""
    if not records:
        return ""
    tiers, series = _grouped_series(records, tier_lookup, "total_runtime_s")
    output_path = os.path.join(output_dir, "latency_by_mode.png")
    return _core.render_grouped_bar_chart(
        tiers,
        series,
        _helpers.MODE_COLORS,
        ylabel="Total Runtime (s, log scale)",
        title="Inference Latency by Model Tier and Mode",
        output_path=output_path,
        log_scale=True,
    )


def render_memory_by_tier_chart(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
    hardware: object,
    output_dir: str,
) -> str:
    """V2: grouped bar chart of peak_ram_mb by tier x mode.

    Draws a "Total RAM" reference line from hardware.ram_gb.
    """
    if not records:
        return ""
    tiers, series = _grouped_series(records, tier_lookup, "peak_ram_mb")
    output_path = os.path.join(output_dir, "memory_by_mode.png")
    ram_mb = hardware.ram_gb * 1024
    return _core.render_grouped_bar_chart(
        tiers,
        series,
        _helpers.MODE_COLORS,
        ylabel="Peak RAM (MB)",
        title="Memory Usage by Model Tier and Mode",
        output_path=output_path,
        reference_line=(ram_mb, "Total RAM"),
    )


def render_vram_by_tier_chart(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
    hardware: object,
    output_dir: str,
) -> str:
    """V7: grouped bar chart of peak_vram_mb by tier x mode.

    Draws a "Total VRAM" reference line from hardware.vram_gb.
    """
    if not records:
        return ""
    tiers, series = _grouped_series(records, tier_lookup, "peak_vram_mb")
    output_path = os.path.join(output_dir, "vram_by_mode.png")
    vram_mb = hardware.vram_gb * 1024
    return _core.render_grouped_bar_chart(
        tiers,
        series,
        _helpers.MODE_COLORS,
        ylabel="Peak VRAM (MB)",
        title="VRAM Usage by Model Tier and Mode",
        output_path=output_path,
        reference_line=(vram_mb, "Total VRAM"),
    )


def render_throughput_chart(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
    output_dir: str,
) -> str:
    """V3: grouped bar chart of generation_throughput by tier x mode.

    Successful runs only.
    """
    successful = [r for r in records if r.status == "success"]
    if not successful:
        return ""
    tiers, series = _grouped_series(successful, tier_lookup, "generation_throughput")
    output_path = os.path.join(output_dir, "throughput_by_mode.png")
    return _core.render_grouped_bar_chart(
        tiers,
        series,
        _helpers.MODE_COLORS,
        ylabel="Throughput (tok/s)",
        title="Generation Throughput by Model Tier and Mode",
        output_path=output_path,
    )
