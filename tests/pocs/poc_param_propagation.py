"""Parameter propagation PoC for all runner types.

Proves each runner forwards model_id, prompt, max_tokens, and
quantization to MetricsCollector.start() before writing final tests.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.sdk.airllm_runner import AirllmRunner
from airllm_benchmark.sdk.cpu_runner import CpuRunner
from airllm_benchmark.sdk.gpu_runner import GpuRunner
from airllm_benchmark.services.metrics import MetricsRecord


def _make_param_record(mode: str, provider: str, quant: str, vram: float = 0.0) -> MetricsRecord:
    """Create a success MetricsRecord for param propagation PoC."""
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
        peak_vram_mb=vram,
        status="success",
        error="",
        timestamp="2024-01-01T00:00:00+00:00",
    )


def poc_params_propagation_gpu() -> None:
    """GPU runner propagates model_id, prompt, max_tokens, quantization."""
    mock_provider = MagicMock()
    mock_provider.generate.return_value = ("output", 10)

    runner = GpuRunner()
    with patch("airllm_benchmark.sdk.gpu_runner.MetricsCollector") as mc:
        mock_col = MagicMock()
        mc.return_value = mock_col
        mock_col.get_record.return_value = _make_param_record(
            "gpu_provider", "p", "8bit", vram=50.0
        )
        runner.run(mock_provider, "hf/model", "my prompt", 64, "8bit")
        mock_col.start.assert_called_once()
        call_kwargs = mock_col.start.call_args[1]
        assert call_kwargs["model_id"] == "hf/model"
        assert call_kwargs["prompt"] == "my prompt"
        assert call_kwargs["max_tokens"] == 64
        assert call_kwargs["quantization"] == "8bit"


def poc_params_propagation_cpu() -> None:
    """CPU runner propagates model_id, prompt, max_tokens, quantization."""
    mock_provider = MagicMock()
    mock_provider.generate.return_value = ("output", 10)

    runner = CpuRunner()
    with patch("airllm_benchmark.sdk.cpu_runner.MetricsCollector") as mc:
        mock_col = MagicMock()
        mc.return_value = mock_col
        mock_col.get_record.return_value = _make_param_record("cpu_baseline", "p", "8bit")
        runner.run(mock_provider, "hf/model", "my prompt", 64, "8bit")
        mock_col.start.assert_called_once()
        call_kwargs = mock_col.start.call_args[1]
        assert call_kwargs["model_id"] == "hf/model"
        assert call_kwargs["prompt"] == "my prompt"
        assert call_kwargs["max_tokens"] == 64
        assert call_kwargs["quantization"] == "8bit"


def poc_params_propagation_airllm() -> None:
    """AirLLM runner propagates model_id, prompt, max_tokens, quantization."""
    runner = AirllmRunner()
    with patch("airllm_benchmark.sdk.airllm_runner.load_model") as ml:
        ml.return_value = MagicMock()
        with patch("airllm_benchmark.sdk.airllm_runner.generate_text") as gt:
            gt.return_value = ("output", 10)
            with patch("airllm_benchmark.sdk.airllm_runner.MetricsCollector") as mc:
                mock_col = MagicMock()
                mc.return_value = mock_col
                mock_col.get_record.return_value = _make_param_record("airllm", "airllm", "8bit")
                runner.run(None, "hf/model", "my prompt", 64, "8bit")
                mock_col.start.assert_called_once()
                call_kwargs = mock_col.start.call_args[1]
                assert call_kwargs["model_id"] == "hf/model"
                assert call_kwargs["prompt"] == "my prompt"
                assert call_kwargs["max_tokens"] == 64
                assert call_kwargs["quantization"] == "8bit"


if __name__ == "__main__":
    from tests.pocs.poc_metrics_output import (
        poc_metrics_success_airllm,
        poc_metrics_success_cpu,
        poc_metrics_success_gpu,
    )
    from tests.pocs.poc_oom_handling import (
        poc_oom_airllm,
        poc_oom_cpu,
        poc_oom_gpu,
    )

    poc_oom_gpu()
    poc_oom_cpu()
    poc_oom_airllm()
    poc_metrics_success_gpu()
    poc_metrics_success_cpu()
    poc_metrics_success_airllm()
    poc_params_propagation_gpu()
    poc_params_propagation_cpu()
    poc_params_propagation_airllm()
    print("[OK] All feature PoCs passed.")
