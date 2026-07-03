"""Unit tests for MetricsCollector edge cases — timing and lifecycle.

Tests timing accuracy, collector reuse, and boundary conditions with
mocked psutil and torch per project rules.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

from airllm_benchmark.services.metrics import MetricsCollector


def _mock_psutil(rss_bytes: int = 50 * 1024 * 1024) -> MagicMock:
    """Return a mocked psutil.Process with deterministic RSS."""
    mock_proc = MagicMock()
    mock_proc.memory_info.return_value.rss = rss_bytes
    return mock_proc


def test_collector_timing_accuracy() -> None:
    """Assert load_time_s reflects elapsed time between start and mark_load_complete."""
    with (
        patch("airllm_benchmark.services.metrics_sampler.psutil") as mock_ps,
        patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.is_available",
            return_value=False,
        ),
    ):
        mock_ps.Process.return_value = _mock_psutil(rss_bytes=10 * 1024 * 1024)

        c = MetricsCollector(sampling_interval=0.1)
        c.start("m", "gpu_provider", "t", "p", "P1", "none", 32)
        c.mark_load_complete()
        time.sleep(0.05)  # Ensure total > load_time
        c.stop()
        record = c.get_record(10, "success")

    assert record.load_time_s > 0
    assert record.total_runtime_s > record.load_time_s
    assert record.ttft_s > 0


def test_collector_reuse_after_stop() -> None:
    """Assert collector can be reused with a new start() call."""
    with (
        patch("airllm_benchmark.services.metrics_sampler.psutil") as mock_ps,
        patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.is_available",
            return_value=False,
        ),
    ):
        mock_ps.Process.return_value = _mock_psutil(rss_bytes=10 * 1024 * 1024)

        c = MetricsCollector(sampling_interval=0.1)
        c.start("m1", "gpu_provider", "t", "p", "P1", "none", 32)
        c.mark_load_complete()
        c.stop()
        r1 = c.get_record(10, "success")

        # Reuse same collector instance
        c.start("m2", "cpu_baseline", "t", "p", "P2", "4bit", 16)
        c.mark_load_complete()
        c.stop()
        r2 = c.get_record(5, "success")

    assert r1.model == "m1"
    assert r2.model == "m2"
    assert r2.mode == "cpu_baseline"


def test_collector_zero_tokens_timeout() -> None:
    """Assert collector records timeout status with zero tokens."""
    with (
        patch("airllm_benchmark.services.metrics_sampler.psutil") as mock_ps,
        patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.is_available",
            return_value=False,
        ),
    ):
        mock_ps.Process.return_value = _mock_psutil(rss_bytes=10 * 1024 * 1024)

        c = MetricsCollector(sampling_interval=0.1)
        c.start("m", "airllm", "t", "p", "P1", "4bit", 32)
        c.stop()
        record = c.get_record(0, "timeout", "Exceeded max runtime")

    assert record.status == "timeout"
    assert record.error == "Exceeded max runtime"
    assert record.tokens_generated == 0
