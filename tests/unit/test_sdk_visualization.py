"""BenchmarkSDK.generate_visualization() tests.

Verifies visualization delegation: VisualizationResult return type,
custom output_dir passthrough, and visualizer interaction.

Per docs/TODO.md task 5.7 — split by interface method.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.metrics import MetricsRecord
from airllm_benchmark.services.visualizer import VisualizationResult


@pytest.fixture
def _record() -> MetricsRecord:
    """Deterministic MetricsRecord for visualization assertions."""
    return MetricsRecord(
        run_id="run_001",
        model="test/small",
        mode="gpu_provider",
        provider="transformers",
        prompt="Hello",
        prompt_id="P1",
        quantization="none",
        max_new_tokens=32,
        load_time_s=0.5,
        ttft_s=0.5,
        total_runtime_s=1.2,
        tokens_generated=20,
        generation_throughput=20.0,
        peak_ram_mb=450.0,
        peak_vram_mb=200.0,
        status="success",
        error="",
        timestamp="2024-01-01T00:00:00+00:00",
    )


class TestGenerateVisualization:
    """BenchmarkSDK.generate_visualization() tests."""

    def test_returns_visualization_result(self, _record: MetricsRecord) -> None:
        """generate_visualization returns VisualizationResult."""
        sdk = BenchmarkSDK()
        sdk._visualizer = MagicMock()
        sdk._visualizer.generate_all.return_value = ["assets/chart.png"]
        sdk._visualizer.generate_table.return_value = "table text"

        result = sdk.generate_visualization([_record])

        assert isinstance(result, VisualizationResult)
        assert result.chart_paths == ["assets/chart.png"]
        assert result.table_text == "table text"

    def test_custom_output_dir(self, _record: MetricsRecord) -> None:
        """generate_visualization passes custom output_dir."""
        sdk = BenchmarkSDK()
        sdk._visualizer = MagicMock()
        sdk._visualizer.generate_all.return_value = []
        sdk._visualizer.generate_table.return_value = ""

        sdk.generate_visualization([_record], output_dir="custom_dir")

        sdk._visualizer.generate_all.assert_called_once()
        call_args = sdk._visualizer.generate_all.call_args
        assert call_args[0][1] == "custom_dir" or call_args.kwargs.get("output_dir") == "custom_dir"
