"""BenchmarkSDK.run_benchmark() tests.

Verifies full-benchmark orchestration: config loading, ResultWriter
lifecycle, runner dispatch via helpers, and visualization generation.

Per docs/TODO.md task 5.7 — split by interface method.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.metrics import MetricsRecord


@pytest.fixture
def _record() -> MetricsRecord:
    """Deterministic MetricsRecord for run_benchmark assertions."""
    return MetricsRecord(
        run_id="r1",
        model="m",
        mode="gpu_provider",
        provider="t",
        prompt="p",
        prompt_id="P1",
        quantization="none",
        max_new_tokens=32,
        load_time_s=1.0,
        ttft_s=1.0,
        total_runtime_s=2.0,
        tokens_generated=10,
        generation_throughput=10.0,
        peak_ram_mb=100.0,
        peak_vram_mb=50.0,
        status="success",
        error="",
        timestamp="2024-01-01T00:00:00+00:00",
    )


class TestRunBenchmark:
    """BenchmarkSDK.run_benchmark() tests."""

    def test_returns_dataclass_with_fields(
        self, mock_config: MagicMock, mock_hw: MagicMock, _record: MetricsRecord
    ) -> None:
        """run_benchmark returns BenchmarkSummaryResult with summary, chart_paths, table_text."""
        with (
            patch("airllm_benchmark.sdk.sdk.load_experiment", return_value=mock_config),
            patch("airllm_benchmark.sdk.sdk.load_hardware", return_value=mock_hw),
            patch("airllm_benchmark.sdk.sdk.validate_hardware"),
            patch("airllm_benchmark.sdk.sdk.ResultWriter") as mock_writer_cls,
            patch("airllm_benchmark.sdk.sdk._helpers._run_benchmark_impl") as mock_impl,
        ):
            mock_writer_cls.return_value = MagicMock()
            mock_impl.return_value = [_record]

            sdk = BenchmarkSDK()
            sdk._visualizer = MagicMock()
            sdk._visualizer.generate_all.return_value = ["assets/chart.png"]
            sdk._visualizer.generate_table.return_value = "table text"

            result = sdk.run_benchmark()

            assert hasattr(result, "summary")
            assert hasattr(result, "chart_paths")
            assert hasattr(result, "table_text")

    def test_writer_cleared_before_run(self, mock_config: MagicMock, mock_hw: MagicMock) -> None:
        """ResultWriter.clear() is called before benchmark runs."""
        with (
            patch("airllm_benchmark.sdk.sdk.load_experiment", return_value=mock_config),
            patch("airllm_benchmark.sdk.sdk.load_hardware", return_value=mock_hw),
            patch("airllm_benchmark.sdk.sdk.validate_hardware"),
            patch("airllm_benchmark.sdk.sdk.ResultWriter") as mock_writer_cls,
            patch("airllm_benchmark.sdk.sdk._helpers._run_benchmark_impl"),
        ):
            writer_instance = MagicMock()
            mock_writer_cls.return_value = writer_instance

            sdk = BenchmarkSDK()
            sdk._visualizer = MagicMock()
            sdk._visualizer.generate_all.return_value = []
            sdk._visualizer.generate_table.return_value = ""

            sdk.run_benchmark()

            writer_instance.clear.assert_called_once()

    def test_visualizer_called_with_records(
        self, mock_config: MagicMock, mock_hw: MagicMock, _record: MetricsRecord
    ) -> None:
        """Visualizer.generate_all() receives all records."""
        with (
            patch("airllm_benchmark.sdk.sdk.load_experiment", return_value=mock_config),
            patch("airllm_benchmark.sdk.sdk.load_hardware", return_value=mock_hw),
            patch("airllm_benchmark.sdk.sdk.validate_hardware"),
            patch("airllm_benchmark.sdk.sdk.ResultWriter"),
            patch("airllm_benchmark.sdk.sdk._helpers._run_benchmark_impl") as mock_impl,
        ):
            mock_impl.return_value = [_record]

            sdk = BenchmarkSDK()
            sdk._visualizer = MagicMock()
            sdk._visualizer.generate_all.return_value = []
            sdk._visualizer.generate_table.return_value = ""

            sdk.run_benchmark()

            sdk._visualizer.generate_all.assert_called_once()
            call_args = sdk._visualizer.generate_all.call_args
            assert call_args[0][0] == [_record]
            # output_dir should be a timestamped subdirectory
            assert call_args[0][1].startswith("assets/run_")
