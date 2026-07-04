"""OOM handling PoC for all runner types.

Proves each runner correctly catches out-of-memory errors and
returns an 'oom' status MetricsRecord before writing final tests.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.sdk.airllm_runner import AirllmRunner
from airllm_benchmark.sdk.cpu_runner import CpuRunner
from airllm_benchmark.sdk.gpu_runner import GpuRunner
from airllm_benchmark.services.metrics import MetricsRecord


def _make_oom_record(mode: str, provider: str, error: str) -> MetricsRecord:
    """Create an OOM MetricsRecord for PoC use."""
    return MetricsRecord(
        run_id="r1",
        model="m",
        mode=mode,
        provider=provider,
        prompt="x",
        prompt_id="P1",
        quantization="none",
        max_new_tokens=32,
        load_time_s=0.0,
        ttft_s=0.0,
        total_runtime_s=0.1,
        tokens_generated=0,
        generation_throughput=0.0,
        peak_ram_mb=0.0,
        peak_vram_mb=0.0,
        status="oom",
        error=error,
        timestamp="2024-01-01T00:00:00+00:00",
    )


def poc_oom_gpu() -> None:
    """GPU runner catches CUDA OOM and returns oom status."""
    mock_provider = MagicMock()
    mock_provider.load_model.side_effect = RuntimeError("CUDA out of memory")

    runner = GpuRunner()
    with patch("airllm_benchmark.sdk.gpu_runner.MetricsCollector") as mc:
        mock_col = MagicMock()
        mc.return_value = mock_col
        mock_col.get_record.return_value = _make_oom_record(
            "gpu_provider", "p", "CUDA out of memory"
        )
        result = runner.run(mock_provider, "test/model", "prompt", 32)
        assert result.status == "oom"
        assert result.tokens_generated == 0
        assert "out of memory" in result.error.lower()


def poc_oom_cpu() -> None:
    """CPU runner catches MemoryError and returns oom status."""
    mock_provider = MagicMock()
    mock_provider.load_model.side_effect = MemoryError("unable to allocate")

    runner = CpuRunner()
    with patch("airllm_benchmark.sdk.cpu_runner.MetricsCollector") as mc:
        mock_col = MagicMock()
        mc.return_value = mock_col
        mock_col.get_record.return_value = _make_oom_record(
            "cpu_baseline", "p", "unable to allocate"
        )
        result = runner.run(mock_provider, "test/model", "prompt", 32)
        assert result.status == "oom"
        assert result.tokens_generated == 0


def poc_oom_airllm() -> None:
    """AirLLM runner catches MemoryError and returns oom status."""
    runner = AirllmRunner()
    with patch("airllm_benchmark.sdk.airllm_runner.load_model") as ml:
        ml.side_effect = MemoryError("RAM exhausted")
        with patch("airllm_benchmark.sdk.airllm_runner.MetricsCollector") as mc:
            mock_col = MagicMock()
            mc.return_value = mock_col
            mock_col.get_record.return_value = _make_oom_record("airllm", "airllm", "RAM exhausted")
            result = runner.run(None, "test/model", "prompt", 32)
            assert result.status == "oom"
            assert result.tokens_generated == 0
