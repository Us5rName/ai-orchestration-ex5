"""Benchmark summary formatting for BenchmarkSDK.

Groups MetricsRecord results by inference mode and produces a
human-readable text summary.  Extracted from sdk_helpers.py to
respect the 150-line file limit.

Per modular-design: Single Responsibility — summary formatting vs.
benchmark orchestration.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from airllm_benchmark.services.metrics import MetricsRecord


@dataclass(frozen=True)
class BenchmarkSummaryResult:
    """Benchmark execution summary with charts and comparison table.

    Returned by BenchmarkSDK.run_benchmark(). Per INTERFACES.md §1.

    Attributes:
        summary: Human-readable summary text grouped by inference mode.
        chart_paths: List of paths to generated chart PNG files.
        table_text: Formatted comparison table as a string.
    """

    summary: str
    chart_paths: list[str]
    table_text: str


def build_summary(records: Sequence[MetricsRecord]) -> str:
    """Build human-readable summary grouped by inference mode.

    Args:
        records: Completed benchmark records from all runs.

    Returns:
        Formatted string with per-mode success counts and average runtime.
    """
    lines: list[str] = [f"Benchmark Summary — {len(records)} runs total"]
    lines.append("-" * 40)

    modes = {"gpu_provider": [], "cpu_baseline": [], "airllm": []}
    for rec in records:
        if rec.mode in modes:
            modes[rec.mode].append(rec)

    for mode, recs in modes.items():
        if not recs:
            continue
        success = sum(1 for r in recs if r.status == "success")
        avg_runtime = sum(r.total_runtime_s for r in recs) / len(recs)
        lines.append(
            f"  {mode}: {len(recs)} runs, {success}/{len(recs)} success, avg {avg_runtime:.2f}s"
        )

    return "\n".join(lines)
