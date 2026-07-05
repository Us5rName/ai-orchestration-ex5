"""Unit tests for the V7 VRAM chart and log-scale latency charts.

Split from test_report_charts.py to stay under the 150-line limit.
Matplotlib Agg backend + tmp dirs, same style as test_report_charts.py.

Run:
    uv run pytest tests/unit/test_report_charts_v7_scale.py -v
"""

from __future__ import annotations

import os
import tempfile
from functools import partial
from typing import TYPE_CHECKING

from airllm_benchmark.services import report_charts, report_helpers
from airllm_benchmark.shared.config_models import HardwareConfig

if TYPE_CHECKING:
    from airllm_benchmark.services.metrics import MetricsRecord
    from airllm_benchmark.shared.config_models import ExperimentConfig


def _hardware() -> HardwareConfig:
    return HardwareConfig(
        cpu="Test CPU",
        gpu="Test GPU 24GB",
        ram_gb=62,
        vram_gb=24,
        disk_free_gb=100,
        os="Test OS",
        documented_by="tester",
        documented_at="2024-01-01T00:00:00+00:00",
    )


class TestVramChart:
    """V7: grouped bar chart of peak_vram_mb by tier x mode."""

    def test_vram_chart_with_reference_line(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_charts.render_vram_by_tier_chart(
                sample_report_records, tier_lookup, _hardware(), tmpdir
            )
            assert os.path.isfile(path)

    def test_vram_chart_skips_on_empty_records(self, report_experiment: ExperimentConfig) -> None:
        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        with tempfile.TemporaryDirectory() as tmpdir:
            assert (
                report_charts.render_vram_by_tier_chart([], tier_lookup, _hardware(), tmpdir) == ""
            )


class TestLatencyChartLogScale:
    """V1 latency chart's log-scale y-axis (GPU vs. CPU-raw span orders of magnitude)."""

    def test_latency_chart_uses_log_scale(
        self,
        sample_report_records: list[MetricsRecord],
        report_experiment: ExperimentConfig,
    ) -> None:
        from airllm_benchmark.services import report_chart_core

        tier_lookup = partial(report_helpers.resolve_tier, experiment=report_experiment)
        captured: dict[str, object] = {}
        original = report_chart_core.render_grouped_bar_chart

        def spy(*args: object, **kwargs: object) -> str:
            captured.update(kwargs)
            return original(*args, **kwargs)

        report_charts._core.render_grouped_bar_chart = spy
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                report_charts.render_latency_by_tier_chart(
                    sample_report_records, tier_lookup, tmpdir
                )
        finally:
            report_charts._core.render_grouped_bar_chart = original

        assert captured.get("log_scale") is True


class TestChartCoreLogScale:
    """render_grouped_bar_chart's log_scale option (used by V1)."""

    def test_log_scale_sets_yscale(self) -> None:
        from airllm_benchmark.services import report_chart_core

        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_chart_core.render_grouped_bar_chart(
                ["small", "medium"],
                {
                    "gpu_provider": [(4.0, True), (6.0, True)],
                    "cpu_baseline": [(139.0, True), (0.0, True)],
                },
                {"gpu_provider": "#2196F3", "cpu_baseline": "#F44336"},
                ylabel="Total Runtime (s)",
                title="test",
                output_path=os.path.join(tmpdir, "out.png"),
                log_scale=True,
            )
            assert os.path.isfile(path)

    def test_log_scale_skipped_when_all_values_zero(self) -> None:
        """Log scale is silently skipped (not an error) when there is
        nothing positive to plot on a log axis."""
        from airllm_benchmark.services import report_chart_core

        with tempfile.TemporaryDirectory() as tmpdir:
            path = report_chart_core.render_grouped_bar_chart(
                ["small"],
                {"gpu_provider": [(0.0, True)]},
                {"gpu_provider": "#2196F3"},
                ylabel="Total Runtime (s)",
                title="test",
                output_path=os.path.join(tmpdir, "out.png"),
                log_scale=True,
            )
            assert os.path.isfile(path)
