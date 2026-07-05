"""Report orchestrator + narrative summary for the reporting layer (§5.3).

New, additive module. Consumes ResultWriter.load() output; produces
the full §5 table, CSV, seven charts, and a hardware-aware narrative.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

from airllm_benchmark.shared.config import load_experiment, load_hardware

from . import report_charts as _charts
from . import report_charts_extra as _charts_extra
from . import report_helpers as _helpers
from . import report_tables as _tables
from .report_narrative import build_narrative_summary

if TYPE_CHECKING:
    from .metrics import MetricsRecord


@dataclass(frozen=True)
class ReportResult:
    """Full report artifacts. Returned by ReportBuilder.build().

    Attributes:
        table_text: Full §5.1 comparison table.
        chart_paths: Absolute paths to the generated V1-V7 chart PNGs
            (empty-data charts are skipped, not included).
        csv_path: Absolute path to the exported metrics CSV.
        summary_text: Hardware-aware narrative summary (§5.3).
    """

    table_text: str
    chart_paths: list[str]
    csv_path: str
    summary_text: str


class ReportBuilder:
    """Builds the full §5 reporting-layer output from metrics records."""

    def build(self, records: list[MetricsRecord], output_dir: str = "assets") -> ReportResult:
        """Build the full report: table, CSV, seven charts, narrative.

        Args:
            records: Metrics records to report on (from ResultWriter.load()).
            output_dir: Directory for CSV + chart PNG output.

        Returns:
            ReportResult with all generated artifacts.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        experiment = load_experiment()
        hardware = load_hardware()
        tier_lookup = partial(_helpers.resolve_tier, experiment=experiment)

        table_text = _tables.format_full_comparison_table(records, tier_lookup)
        csv_path = _tables.export_metrics_csv(
            records, tier_lookup, str(Path(output_dir) / "metrics.csv")
        )

        chart_paths = [
            path
            for path in [
                _charts.render_latency_by_tier_chart(records, tier_lookup, output_dir),
                _charts.render_memory_by_tier_chart(records, tier_lookup, hardware, output_dir),
                _charts.render_throughput_chart(records, tier_lookup, output_dir),
                _charts_extra.render_latency_breakdown_chart(records, tier_lookup, output_dir),
                _charts_extra.render_prompt_sensitivity_chart(records, output_dir),
                _charts_extra.render_memory_vs_throughput_scatter(records, tier_lookup, output_dir),
                _charts.render_vram_by_tier_chart(records, tier_lookup, hardware, output_dir),
            ]
            if path
        ]

        summary_text = build_narrative_summary(records, hardware, tier_lookup)

        return ReportResult(
            table_text=table_text,
            chart_paths=chart_paths,
            csv_path=csv_path,
            summary_text=summary_text,
        )


def derive_report_output_dir(results_path: str, assets_root: str = "assets") -> str:
    """Derive a per-run report output directory from a results file path.

    Reuses the ``assets/run_<timestamp>/`` directory from that run if it
    already exists (colocating the report with its run); otherwise falls
    back to a fresh ``assets/report_<timestamp>/`` directory. Never
    overwrites a shared flat ``assets/`` across runs.

    Args:
        results_path: Path to a ``metrics_<timestamp>.json`` results file.
        assets_root: Root assets directory (default: "assets").

    Returns:
        Directory path for this report's table/CSV/chart output.
    """
    stem = Path(results_path).stem
    match = re.match(r"metrics_(.+)", stem)
    timestamp = match.group(1) if match else stem

    run_dir = Path(assets_root) / f"run_{timestamp}"
    if run_dir.is_dir():
        return str(run_dir)
    return str(Path(assets_root) / f"report_{timestamp}")

