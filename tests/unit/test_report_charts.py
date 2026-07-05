"""Unit tests for the report-layer V1-V6 charts.

Matplotlib Agg backend + tmp dirs, same style as
test_visualizer_charts.py. Nothing external is mocked.

Run:
    uv run pytest tests/unit/test_report_charts.py -v
"""

from __future__ import annotations

import os
import tempfile
from functools import partial
from typing import TYPE_CHECKING

from airllm_benchmark.services import report_charts, report_charts_extra, report_helpers
from airllm_benchmark.shared.config_models import HardwareConfig

if TYPE_CHECKING:
    from airllm_benchmark.services.metrics import MetricsRecord
    from airllm_benchmark.shared.config_models import ExperimentConfig


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


class TestGroupedCharts:
    """V1-V3: latency / memory / throughput grouped bar charts."""

    def test_latency_chart_returns_existing_png(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_charts.render_latency_by_tier_chart(
                sample_report_records, tier_lookup, tmpdir
            )
            assert os.path.isabs(path)
            assert os.path.isfile(path)

    def test_memory_chart_with_reference_line(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_charts.render_memory_by_tier_chart(
                sample_report_records, tier_lookup, _hardware(), tmpdir
            )
            assert os.path.isfile(path)

    def test_throughput_chart_successful_only(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_charts.render_throughput_chart(
                sample_report_records, tier_lookup, tmpdir
            )
            assert os.path.isfile(path)

    def test_empty_records_skip_gracefully(self, report_experiment: ExperimentConfig) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            assert report_charts.render_latency_by_tier_chart([], tier_lookup, tmpdir) == ""


class TestExtraCharts:
    """V4-V6: latency breakdown, prompt sensitivity, memory-vs-throughput."""

    def test_latency_breakdown_returns_existing_png(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_charts_extra.render_latency_breakdown_chart(
                sample_report_records, tier_lookup, tmpdir
            )
            assert os.path.isfile(path)

    def test_prompt_sensitivity_renders_with_distinct_prompt_ids(
        self,
        sample_report_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_charts_extra.render_prompt_sensitivity_chart(
                sample_report_records, tmpdir
            )
            assert os.path.isfile(path)

    def test_prompt_sensitivity_skips_on_empty_prompt_id(
        self,
        empty_prompt_id_records: list[MetricsRecord],
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_charts_extra.render_prompt_sensitivity_chart(
                empty_prompt_id_records, tmpdir
            )
            assert path == ""

    def test_memory_vs_throughput_scatter(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_charts_extra.render_memory_vs_throughput_scatter(
                sample_report_records, tier_lookup, tmpdir
            )
            assert os.path.isfile(path)

    def test_oom_record_does_not_crash_any_chart(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        """sample_report_records already includes an oom record (run_004)."""
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            assert report_charts.render_latency_by_tier_chart(
                sample_report_records, tier_lookup, tmpdir
            )
            assert report_charts.render_memory_by_tier_chart(
                sample_report_records, tier_lookup, _hardware(), tmpdir
            )
            assert report_charts_extra.render_latency_breakdown_chart(
                sample_report_records, tier_lookup, tmpdir
            )
            assert report_charts_extra.render_memory_vs_throughput_scatter(
                sample_report_records, tier_lookup, tmpdir
            )
