"""V4-V5 charts for the reporting layer (§5.2).

Split from report_charts.py to stay under the 150-line limit. V6-V7
(scatter charts) live in report_charts_scatter.py. Uses matplotlib
directly for the stacked/line forms not covered by
report_chart_core's grouped-bar renderer.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import report_chart_core as _core
from . import report_helpers as _helpers

if TYPE_CHECKING:
    from collections.abc import Callable

    from .metrics import MetricsRecord


def render_latency_breakdown_chart(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
    output_dir: str,
) -> str:
    """V4: stacked bar of load_time_s / ttft_s / generation time by tier x mode."""
    if not records:
        return ""

    groups = _helpers.group_by_tier_and_mode(records, tier_lookup)
    keys = _helpers.sorted_group_keys(groups)
    labels = [f"{tier}\n{mode}" for tier, mode in keys]

    load_vals, ttft_vals, gen_vals = [], [], []
    for key in keys:
        recs = groups[key]
        n = len(recs)
        load_vals.append(sum(r.load_time_s for r in recs) / n)
        ttft_vals.append(sum(r.ttft_s for r in recs) / n)
        gen_vals.append(sum(max(r.total_runtime_s - r.ttft_s, 0.0) for r in recs) / n)

    segments = {"Load": load_vals, "TTFT": ttft_vals, "Generation": gen_vals}
    colors = {"Load": "#9E9E9E", "TTFT": "#FFC107", "Generation": "#3F51B5"}
    output_path = os.path.join(output_dir, "latency_breakdown.png")
    return _core.render_stacked_bar_chart(
        labels,
        segments,
        colors,
        ylabel="Time (s)",
        title="Latency Breakdown by Model Tier and Mode",
        output_path=output_path,
    )


def render_prompt_sensitivity_chart(
    records: list[MetricsRecord],
    output_dir: str,
) -> str:
    """V5: line chart of total_runtime_s by prompt_id, one line per (model, mode).

    Skips (returns "") when every record has an empty prompt_id.
    """
    if not records or all(r.prompt_id == "" for r in records):
        return ""

    series: dict[tuple[str, str], dict[str, float]] = {}
    prompt_ids: set[str] = set()
    for r in records:
        key = (r.model, r.mode)
        series.setdefault(key, {})[r.prompt_id] = r.total_runtime_s
        prompt_ids.add(r.prompt_id)

    x_labels = sorted(prompt_ids)
    fig, ax = plt.subplots(figsize=(10, 6))
    for (model, mode), by_prompt in series.items():
        y = [by_prompt.get(pid, float("nan")) for pid in x_labels]
        ax.plot(
            x_labels,
            y,
            marker="o",
            label=f"{model} / {mode}",
            color=_helpers.MODE_COLORS.get(mode, "#9E9E9E"),
        )

    ax.set_ylabel("Total Runtime (s)", fontsize=11)
    ax.set_title("Prompt Sensitivity by Model and Mode", fontsize=13)
    ax.tick_params(axis="both", labelsize=10)
    ax.legend(fontsize=8)

    output_path = os.path.join(output_dir, "prompt_sensitivity.png")
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)


