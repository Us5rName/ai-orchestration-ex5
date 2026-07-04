"""BenchmarkSDK module PoC.

Exercises all three BenchmarkSDK interface methods with real config
loaded from config/experiment.json and mocked runners so the
orchestration flow is proven without requiring actual model inference.

Per IMPLEMENTATION.md Step 3 — PoC after full module.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.metrics import MetricsRecord
from airllm_benchmark.services.visualizer import VisualizationResult

POC_DIR = Path(__file__).resolve().parent.parent
REAL_CONFIG = POC_DIR / "config"


def _make_record(mode: str, provider: str) -> MetricsRecord:
    """Create a deterministic MetricsRecord for PoC assertions."""
    return MetricsRecord(
        run_id=f"poc_{mode}",
        model="test/small",
        mode=mode,
        provider=provider,
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


# ——— PoC: run_single ———


def test_poc_run_single() -> None:
    """SDK.run_single dispatches to runner and returns MetricsRecord."""
    expected = _make_record("gpu_provider", "transformers")
    mock_runner = MagicMock()
    mock_runner.run.return_value = expected

    sdk = BenchmarkSDK(config_dir=REAL_CONFIG)
    sdk._runner_mgr = MagicMock()
    sdk._runner_mgr.get_runner.return_value = mock_runner

    result = sdk.run_single(
        model_id="test/small",
        mode="gpu_provider",
        prompt="Hello",
    )

    assert isinstance(result, MetricsRecord)
    assert result.status == "success"
    assert result.mode == "gpu_provider"
    mock_runner.run.assert_called_once()


# ——— PoC: run_benchmark ———


def test_poc_run_benchmark() -> None:
    """SDK.run_benchmark orchestrates full pipeline and returns summary dict."""
    mock_hw = MagicMock()
    mock_hw.is_complete.return_value = True

    with (
        patch("airllm_benchmark.sdk.sdk.load_hardware", return_value=mock_hw),
        patch("airllm_benchmark.sdk.sdk.validate_hardware"),
        patch("airllm_benchmark.sdk.sdk.ResultWriter") as mock_writer_cls,
        patch("airllm_benchmark.sdk.sdk._helpers._run_benchmark_impl") as mock_impl,
    ):
        writer_instance = MagicMock()
        mock_writer_cls.return_value = writer_instance
        mock_impl.return_value = [
            _make_record("gpu_provider", "transformers"),
            _make_record("cpu_baseline", "transformers"),
            _make_record("airllm", "airllm"),
        ]

        sdk = BenchmarkSDK(config_dir=REAL_CONFIG)
        sdk._visualizer = MagicMock()
        sdk._visualizer.generate_all.return_value = ["assets/latency.png", "assets/memory.png"]
        sdk._visualizer.generate_table.return_value = "mode | runtime\n"

        result = sdk.run_benchmark()

        # Verify ResultWriter lifecycle
        writer_instance.clear.assert_called_once()

        # Verify return contract: dict with summary, chart_paths, table_text
        assert isinstance(result, dict)
        assert "summary" in result
        assert "chart_paths" in result
        assert "table_text" in result
        assert isinstance(result["summary"], str)
        assert isinstance(result["chart_paths"], list)
        assert isinstance(result["table_text"], str)


# ——— PoC: generate_visualization ———


def test_poc_generate_visualization() -> None:
    """SDK.generate_visualization returns VisualizationResult."""
    sdk = BenchmarkSDK(config_dir=REAL_CONFIG)
    sdk._visualizer = MagicMock()
    sdk._visualizer.generate_all.return_value = ["assets/chart.png"]
    sdk._visualizer.generate_table.return_value = "table"

    records = [_make_record("gpu_provider", "transformers")]
    result = sdk.generate_visualization(records)

    assert isinstance(result, VisualizationResult)
    assert len(result.chart_paths) >= 1
    assert result.table_text == "table"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
