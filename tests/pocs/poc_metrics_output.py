"""Metrics output PoC for all runner types.

Proves each runner returns a valid MetricsRecord with correct
fields on successful inference before writing final tests.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.sdk.airllm_runner import AirllmRunner
from airllm_benchmark.sdk.cpu_runner import CpuRunner
from airllm_benchmark.sdk.gpu_runner import GpuRunner
from airllm_benchmark.services.metrics import MetricsRecord


def _make_success_record(
    mode: str,
    provider: str,
    tokens: int = 15,
    vram: float = 0.0,
    quant: str = "none",
) -> MetricsRecord:
    """Create a success MetricsRecord for PoC use."""
    return MetricsRecord(
        run_id="r1",
        model="test/model",
        mode=mode,
        provider=provider,
        prompt="hello",
        prompt_id="P1",
        quantization=quant,
        max_new_tokens=32,
        load_time_s=0.5,
        ttft_s=0.5,
        total_runtime_s=1.0,
        tokens_generated=tokens,
        generation_throughput=float(tokens),
        peak_ram_mb=100.0,
        peak_vram_mb=vram,
        status="success",
        error="",
        timestamp="2024-01-01T00:00:00+00:00",
    )


def poc_metrics_success_gpu() -> None:
    """GPU runner returns MetricsRecord with correct fields on success."""
    mock_provider = MagicMock()
    mock_provider.generate.return_value = ("output", 15)

    runner = GpuRunner()
    with patch("airllm_benchmark.sdk.gpu_runner.MetricsCollector") as mc:
        mock_col = MagicMock()
        mc.return_value = mock_col
        mock_col.get_record.return_value = _make_success_record(
            "gpu_provider", "transformers", vram=50.0
        )
        result = runner.run(mock_provider, "test/model", "hello", 32)
        assert isinstance(result, MetricsRecord)
        assert result.tokens_generated == 15
        assert result.status == "success"
        assert result.error == ""


def poc_metrics_success_cpu() -> None:
    """CPU runner returns MetricsRecord with correct fields on success."""
    mock_provider = MagicMock()
    mock_provider.generate.return_value = ("output", 15)

    runner = CpuRunner()
    with patch("airllm_benchmark.sdk.cpu_runner.MetricsCollector") as mc:
        mock_col = MagicMock()
        mc.return_value = mock_col
        mock_col.get_record.return_value = _make_success_record("cpu_baseline", "transformers")
        result = runner.run(mock_provider, "test/model", "hello", 32)
        assert isinstance(result, MetricsRecord)
        assert result.tokens_generated == 15
        assert result.status == "success"


def poc_metrics_success_airllm() -> None:
    """AirLLM runner returns MetricsRecord with correct fields on success."""
    runner = AirllmRunner()
    with patch("airllm_benchmark.sdk.airllm_runner.load_model") as ml:
        ml.return_value = MagicMock()
        with patch("airllm_benchmark.sdk.airllm_runner.generate_text") as gt:
            gt.return_value = ("output", 15)
            with patch("airllm_benchmark.sdk.airllm_runner.MetricsCollector") as mc:
                mock_col = MagicMock()
                mc.return_value = mock_col
                mock_col.get_record.return_value = _make_success_record(
                    "airllm", "airllm", quant="4bit"
                )
                result = runner.run(None, "test/model", "hello", 32, "4bit")
                assert isinstance(result, MetricsRecord)
                assert result.tokens_generated == 15
                assert result.status == "success"
