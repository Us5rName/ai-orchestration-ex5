"""Unit tests for services/metrics.py — MetricsCollector + MetricsRecord.

All external dependencies (psutil, torch) are mocked per project rules.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.services.metrics import MetricsCollector, MetricsRecord


def _mock_psutil(rss_bytes: int = 50 * 1024 * 1024) -> MagicMock:
    """Return a mocked psutil.Process with deterministic RSS."""
    mock_proc = MagicMock()
    mock_proc.memory_info.return_value.rss = rss_bytes
    return mock_proc


def test_record_contains_all_fields() -> None:
    """Assert MetricsRecord has all 17 fields from CONFIG.md §1."""
    record = MetricsRecord(
        run_id="run_001",
        model="test-model",
        mode="gpu_provider",
        provider="transformers",
        prompt="hello",
        prompt_id="P1",
        quantization="4bit",
        max_new_tokens=32,
        load_time_s=1.0,
        ttft_s=2.0,
        total_runtime_s=3.0,
        tokens_generated=10,
        peak_ram_mb=100.0,
        peak_vram_mb=200.0,
        status="success",
        error="",
        timestamp="2026-01-01T00:00:00+00:00",
    )
    assert record.run_id == "run_001"
    assert record.model == "test-model"
    assert record.mode == "gpu_provider"
    assert record.tokens_generated == 10
    assert record.peak_ram_mb == 100.0
    assert record.status == "success"


def test_record_is_frozen() -> None:
    """Assert MetricsRecord cannot be mutated after creation."""
    record = MetricsRecord(
        run_id="r1",
        model="m",
        mode="gpu_provider",
        provider="t",
        prompt="p",
        prompt_id="P1",
        quantization="none",
        max_new_tokens=1,
        load_time_s=0.0,
        ttft_s=0.0,
        total_runtime_s=0.0,
        tokens_generated=0,
        peak_ram_mb=0.0,
        peak_vram_mb=0.0,
        status="success",
        error="",
        timestamp="2026-01-01T00:00:00+00:00",
    )
    try:
        record.status = "oom"  # type: ignore[frozen-instantiation]
        assert False, "Expected FrozenInstanceError"
    except Exception:
        pass  # Expected — dataclass is frozen


def test_collector_full_lifecycle() -> None:
    """Assert collector produces a valid record through full lifecycle."""
    with (
        patch("airllm_benchmark.services.metrics_sampler.psutil") as mock_ps,
        patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.is_available",
            return_value=False,
        ),
    ):
        mock_ps.Process.return_value = _mock_psutil(rss_bytes=64 * 1024 * 1024)

        c = MetricsCollector(sampling_interval=0.2)
        c.start(
            model_id="test-model",
            mode="gpu_provider",
            provider="transformers",
            prompt="hello",
            prompt_id="P1",
            quantization="4bit",
            max_tokens=32,
        )
        c.mark_load_complete()
        c.stop()
        record = c.get_record(tokens_generated=10, status="success")

    assert record.model == "test-model"
    assert record.mode == "gpu_provider"
    assert record.provider == "transformers"
    assert record.prompt_id == "P1"
    assert record.quantization == "4bit"
    assert record.max_new_tokens == 32
    assert record.tokens_generated == 10
    assert record.status == "success"
    assert record.error == ""
    assert record.load_time_s > 0
    assert record.total_runtime_s > 0
    assert record.peak_ram_mb > 0


def test_collector_error_record() -> None:
    """Assert collector captures error status and message."""
    with (
        patch("airllm_benchmark.services.metrics_sampler.psutil") as mock_ps,
        patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.is_available",
            return_value=False,
        ),
    ):
        mock_ps.Process.return_value = _mock_psutil(rss_bytes=32 * 1024 * 1024)

        c = MetricsCollector(sampling_interval=0.1)
        c.start("m", "cpu_baseline", "t", "p", "P2", "none", 16)
        c.stop()
        record = c.get_record(
            tokens_generated=0,
            status="oom",
            error="CUDA out of memory",
        )

    assert record.status == "oom"
    assert record.error == "CUDA out of memory"
    assert record.tokens_generated == 0


def test_collector_no_cuda_returns_zero_vram() -> None:
    """Assert peak_vram_mb is 0.0 when CUDA is unavailable."""
    with (
        patch("airllm_benchmark.services.metrics_sampler.psutil") as mock_ps,
        patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.is_available",
            return_value=False,
        ),
    ):
        mock_ps.Process.return_value = _mock_psutil(rss_bytes=10 * 1024 * 1024)

        c = MetricsCollector(sampling_interval=0.1)
        c.start("m", "airllm", "t", "p", "P3", "8bit", 64)
        c.stop()
        record = c.get_record(5, "success")

    assert record.peak_vram_mb == 0.0


def test_collector_cuda_vram_tracking() -> None:
    """Assert peak_vram_mb reflects CUDA allocation when available."""
    with (
        patch("airllm_benchmark.services.metrics_sampler.psutil") as mock_ps,
        patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.is_available",
            return_value=True,
        ),
    ):
        mock_ps.Process.return_value = _mock_psutil(rss_bytes=20 * 1024 * 1024)
        # Mock peak VRAM = 500 MB
        mock_max_alloc = patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.max_memory_allocated",
            return_value=500 * 1024 * 1024,
        )
        mock_reset = patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.reset_peak_memory_stats"
        )

        with mock_reset, mock_max_alloc:
            c = MetricsCollector(sampling_interval=0.1)
            c.start("m", "gpu_provider", "t", "p", "P1", "none", 32)
            c.stop()
            record = c.get_record(20, "success")

    assert record.peak_vram_mb == 500.0
