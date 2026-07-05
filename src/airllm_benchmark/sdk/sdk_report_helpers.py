"""Helper for BenchmarkSDK.generate_report — keeps sdk.py under 150 lines.

Per docs/INTERFACES.md §11 (Report Builder).
"""

from __future__ import annotations

from pathlib import Path

from airllm_benchmark.services.report_builder import (
    ReportBuilder,
    ReportResult,
    derive_report_output_dir,
)
from airllm_benchmark.services.result_writer import ResultWriter


def generate_report(
    results_path: str,
    output_dir: str | None,
    config_dir: str | None = None,
) -> ReportResult:
    """Load persisted results and build the full §5 report.

    Args:
        results_path: Path to a persisted metrics JSON file
            (as written by ResultWriter, e.g. "results/metrics_<ts>.json").
        output_dir: Directory for report artifacts, or None to derive a
            per-run subdirectory from results_path (reusing
            assets/run_<ts>/ if present, else assets/report_<ts>/).
        config_dir: Optional config directory override so the report uses
            the same experiment config that produced the metrics.

    Returns:
        ReportResult with table_text, chart_paths, csv_path, summary_text.
    """
    records = ResultWriter(results_path).load()
    resolved_dir = output_dir or derive_report_output_dir(results_path)
    return ReportBuilder().build(
        records,
        output_dir=resolved_dir,
        config_dir=Path(config_dir) if config_dir else None,
    )
