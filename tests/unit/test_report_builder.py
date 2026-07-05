"""Unit tests for ReportBuilder + build_narrative_summary.

Uses the project's real config/experiment.json and config/hardware.json
(read-only) — same convention as other SDK-level tests that don't mock
config loading. Matplotlib Agg backend + tmp dirs; nothing external
is mocked.

Run:
    uv run pytest tests/unit/test_report_builder.py -v
"""

from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING

from airllm_benchmark.services.report_builder import ReportBuilder, ReportResult
from airllm_benchmark.services.report_narrative import build_narrative_summary
from airllm_benchmark.shared.config_models import HardwareConfig

if TYPE_CHECKING:
    from airllm_benchmark.services.metrics import MetricsRecord


def _hardware() -> HardwareConfig:
    return HardwareConfig(
        cpu="Test CPU",
        gpu="Test GPU 24GB",
        ram_gb=62,
        disk_free_gb=100,
        os="Test OS",
        documented_by="tester",
        documented_at="2024-01-01T00:00:00+00:00",
    )


class TestReportBuilder:
    """ReportBuilder.build orchestrates table, CSV, charts, and narrative."""

    def test_returns_report_result(
        self,
        sample_report_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ReportBuilder().build(sample_report_records, output_dir=tmpdir)
            assert isinstance(result, ReportResult)

    def test_csv_path_exists(
        self,
        sample_report_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ReportBuilder().build(sample_report_records, output_dir=tmpdir)
            assert os.path.isfile(result.csv_path)

    def test_chart_paths_all_exist(
        self,
        sample_report_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ReportBuilder().build(sample_report_records, output_dir=tmpdir)
            assert result.chart_paths
            for path in result.chart_paths:
                assert os.path.isfile(path)

    def test_table_text_non_empty(
        self,
        sample_report_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ReportBuilder().build(sample_report_records, output_dir=tmpdir)
            assert "Model" in result.table_text

    def test_empty_records_all_charts_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ReportBuilder().build([], output_dir=tmpdir)
            assert result.chart_paths == []


class TestBuildNarrativeSummary:
    """build_narrative_summary produces a hardware-aware, mode-aware text."""

    def test_contains_hardware_strings(
        self,
        sample_report_records: list[MetricsRecord],
    ) -> None:
        hw = _hardware()
        summary = build_narrative_summary(sample_report_records, hw, lambda _m: "small")
        assert hw.cpu in summary
        assert hw.gpu in summary
        assert str(hw.ram_gb) in summary

    def test_contains_mode_names(
        self,
        sample_report_records: list[MetricsRecord],
    ) -> None:
        summary = build_narrative_summary(sample_report_records, _hardware(), lambda _m: "small")
        assert "gpu_provider" in summary
        assert "cpu_baseline" in summary
        assert "airllm" in summary

    def test_flags_oom_anomaly(
        self,
        sample_report_records: list[MetricsRecord],
    ) -> None:
        summary = build_narrative_summary(sample_report_records, _hardware(), lambda _m: "large")
        assert "run_004" in summary

    def test_empty_records_returns_placeholder(self) -> None:
        assert build_narrative_summary([], _hardware(), lambda _m: "unknown") == (
            "No records to summarize."
        )
