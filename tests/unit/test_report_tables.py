"""Unit tests for the report-layer full table + CSV export.

Run:
    uv run pytest tests/unit/test_report_tables.py -v
"""

from __future__ import annotations

import csv
import os
import tempfile
from functools import partial
from typing import TYPE_CHECKING

from airllm_benchmark.services import report_helpers, report_tables

if TYPE_CHECKING:
    from airllm_benchmark.services.metrics import MetricsRecord
    from airllm_benchmark.shared.config_models import ExperimentConfig


class TestFormatFullComparisonTable:
    """format_full_comparison_table produces the full §5.1 column set."""

    def test_all_required_headers_present(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        table = report_tables.format_full_comparison_table(sample_report_records, tier_lookup)
        for header in [
            "Model",
            "Tier",
            "Mode",
            "Load (s)",
            "TTFT (s)",
            "Runtime (s)",
            "Throughput (tok/s)",
            "Peak RAM (MB)",
            "Peak VRAM (MB)",
            "Status",
        ]:
            assert header in table

    def test_empty_records_returns_placeholder(self) -> None:
        assert report_tables.format_full_comparison_table([], lambda _m: "unknown") == (
            "No records to display."
        )

    def test_tier_resolved_per_row(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        table = report_tables.format_full_comparison_table(sample_report_records, tier_lookup)
        assert "small" in table
        assert "medium" in table
        assert "large" in table

    def test_oom_status_present(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        table = report_tables.format_full_comparison_table(sample_report_records, tier_lookup)
        assert "oom" in table


class TestExportMetricsCsv:
    """export_metrics_csv writes all 18 fields + derived tier."""

    def test_returns_absolute_path(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_tables.export_metrics_csv(
                sample_report_records, tier_lookup, os.path.join(tmpdir, "metrics.csv")
            )
            assert os.path.isabs(path)
            assert os.path.isfile(path)

    def test_row_count_matches_records(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_tables.export_metrics_csv(
                sample_report_records, tier_lookup, os.path.join(tmpdir, "metrics.csv")
            )
            with open(path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            assert len(rows) == len(sample_report_records)

    def test_columns_include_all_fields_plus_tier(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_tables.export_metrics_csv(
                sample_report_records, tier_lookup, os.path.join(tmpdir, "metrics.csv")
            )
            with open(path, newline="", encoding="utf-8") as f:
                header = next(csv.reader(f))
            assert "tier" in header
            assert "run_id" in header
            assert "peak_vram_mb" in header
            assert len(header) == 19  # 18 MetricsRecord fields + tier
