"""Cross-runner parameter propagation tests.

Verifies all runners forward model_id, prompt, max_tokens, and
quantization to MetricsCollector.start() correctly.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.sdk.airllm_runner import AirllmRunner
from airllm_benchmark.sdk.cpu_runner import CpuRunner
from airllm_benchmark.sdk.gpu_runner import GpuRunner
from airllm_benchmark.services.metrics import MetricsRecord


def _make_param_record(mode: str, provider: str, quant: str) -> MetricsRecord:
    """Create a success MetricsRecord for parameter propagation tests."""
    return MetricsRecord(
        run_id="r1",
        model="m",
        mode=mode,
        provider=provider,
        prompt="x",
        prompt_id="P1",
        quantization=quant,
        max_new_tokens=64,
        load_time_s=0.5,
        ttft_s=0.5,
        total_runtime_s=1.0,
        tokens_generated=10,
        generation_throughput=10.0,
        peak_ram_mb=100.0,
        peak_vram_mb=50.0 if mode == "gpu_provider" else 0.0,
        status="success",
        error="",
        timestamp="2024-01-01T00:00:00+00:00",
    )


class TestCrossRunnerParams:
    """All runners propagate parameters to MetricsCollector.start()."""

    def test_gpu_propagates_all_params(self) -> None:
        """GPU runner forwards model_id, prompt, max_tokens, quantization."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = ("out", 10)
        runner = GpuRunner()
        with patch("airllm_benchmark.sdk.gpu_runner.MetricsCollector") as mc:
            mock_col = MagicMock()
            mc.return_value = mock_col
            mock_col.get_record.return_value = _make_param_record("gpu_provider", "p", "8bit")
            runner.run(mock_provider, "hf/model", "hello", 64, "8bit")
            kw = mock_col.start.call_args[1]
            assert kw["model_id"] == "hf/model"
            assert kw["prompt"] == "hello"
            assert kw["max_tokens"] == 64
            assert kw["quantization"] == "8bit"

    def test_cpu_propagates_all_params(self) -> None:
        """CPU runner forwards model_id, prompt, max_tokens, quantization."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = ("out", 10)
        runner = CpuRunner()
        with patch("airllm_benchmark.sdk.cpu_runner.MetricsCollector") as mc:
            mock_col = MagicMock()
            mc.return_value = mock_col
            mock_col.get_record.return_value = _make_param_record("cpu_baseline", "p", "8bit")
            runner.run(mock_provider, "hf/model", "hello", 64, "8bit")
            kw = mock_col.start.call_args[1]
            assert kw["model_id"] == "hf/model"
            assert kw["prompt"] == "hello"
            assert kw["max_tokens"] == 64
            assert kw["quantization"] == "8bit"

    def test_airllm_propagates_all_params(self) -> None:
        """AirLLM runner forwards model_id, prompt, max_tokens, quantization."""
        runner = AirllmRunner()
        with patch("airllm_benchmark.sdk.airllm_runner.load_model") as ml:
            ml.return_value = MagicMock()
            with patch("airllm_benchmark.sdk.airllm_runner.generate_text") as gt:
                gt.return_value = ("out", 10)
                with patch("airllm_benchmark.sdk.airllm_runner.MetricsCollector") as mc:
                    mock_col = MagicMock()
                    mc.return_value = mock_col
                    mock_col.get_record.return_value = _make_param_record(
                        "airllm", "airllm", "8bit"
                    )
                    runner.run(None, "hf/model", "hello", 64, "8bit")
                    kw = mock_col.start.call_args[1]
                    assert kw["model_id"] == "hf/model"
                    assert kw["prompt"] == "hello"
                    assert kw["max_tokens"] == 64
                    assert kw["quantization"] == "8bit"
