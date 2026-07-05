"""Unit tests for MetricsCollector.mark_first_token — real TTFT semantics.

Split from test_metrics_collector.py to stay under the 150-line limit.
All external dependencies (psutil, torch) are mocked per project rules.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.services.metrics import MetricsCollector


def _mock_psutil(rss_bytes: int = 50 * 1024 * 1024) -> MagicMock:
    """Return a mocked psutil.Process with deterministic RSS."""
    mock_proc = MagicMock()
    mock_proc.memory_info.return_value.rss = rss_bytes
    return mock_proc


def test_collector_no_first_token_reports_unmeasured_ttft() -> None:
    """Assert ttft_s is 0.0 when the provider never calls mark_first_token.

    Real TTFT is only known for providers with a per-token callback; for
    everyone else it must read as "unmeasured", not fall back to load or
    setup time (see docs/INTERFACES.md metrics section).
    """
    with (
        patch("airllm_benchmark.services.metrics_sampler.psutil") as mock_ps,
        patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.is_available",
            return_value=False,
        ),
    ):
        mock_ps.Process.return_value = _mock_psutil(rss_bytes=64 * 1024 * 1024)

        c = MetricsCollector(sampling_interval=0.2)
        c.start("m", "cpu_baseline", "transformers", "hello", "P1", "none", 32)
        c.mark_load_complete()
        c.mark_generation_start()
        c.stop()
        record = c.get_record(tokens_generated=10, status="success")

    assert record.ttft_s == 0.0
    assert record.load_time_s > 0
