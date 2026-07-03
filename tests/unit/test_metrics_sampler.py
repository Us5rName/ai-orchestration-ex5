"""Unit tests for RamSampler and VramTracker — memory sampling internals.

Tests timing accuracy, memory sampling, and peak calculation with mocked
psutil and torch per project rules.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

from airllm_benchmark.services.metrics_sampler import RamSampler, VramTracker

# ---------------------------------------------------------------------------
# RamSampler tests
# ---------------------------------------------------------------------------


def test_ram_sampler_peak_from_samples() -> None:
    """Assert peak_mb returns the maximum RSS across all samples."""
    with patch("airllm_benchmark.services.metrics_sampler.psutil") as mock_ps:
        # Simulate increasing RSS: 30MB -> 60MB -> 45MB -> peak = 60MB
        rss_values = [
            30 * 1024 * 1024,
            60 * 1024 * 1024,
            45 * 1024 * 1024,
        ]
        mock_proc = MagicMock()
        mock_proc.memory_info.return_value.rss = rss_values[0]
        mock_ps.Process.return_value = mock_proc

        sampler = RamSampler(interval=0.05)
        sampler.start()
        time.sleep(0.06)  # Allow first sample

        # Change RSS to second value
        mock_proc.memory_info.return_value.rss = rss_values[1]
        time.sleep(0.06)

        # Change RSS to third value
        mock_proc.memory_info.return_value.rss = rss_values[2]
        time.sleep(0.06)
        sampler.stop()

    peak = sampler.peak_mb()
    # Peak should be close to 60 MB (the highest sample)
    assert 55.0 <= peak <= 65.0


def test_ram_sampler_zero_peak_when_stopped() -> None:
    """Assert peak_mb returns 0.0 before any sampling occurs."""
    sampler = RamSampler(interval=0.05)
    assert sampler.peak_mb() == 0.0


def test_ram_sampler_single_sample() -> None:
    """Assert peak_mb reflects a single sample correctly."""
    with patch("airllm_benchmark.services.metrics_sampler.psutil") as mock_ps:
        expected_rss = 25 * 1024 * 1024
        mock_proc = MagicMock()
        mock_proc.memory_info.return_value.rss = expected_rss
        mock_ps.Process.return_value = mock_proc

        sampler = RamSampler(interval=0.05)
        sampler.start()
        time.sleep(0.06)  # Allow one sample
        sampler.stop()

    peak = sampler.peak_mb()
    assert 24.0 <= peak <= 26.0


def test_ram_sampler_multiple_stops_idempotent() -> None:
    """Assert calling stop() multiple times does not raise."""
    with patch("airllm_benchmark.services.metrics_sampler.psutil") as mock_ps:
        mock_proc = MagicMock()
        mock_proc.memory_info.return_value.rss = 10 * 1024 * 1024
        mock_ps.Process.return_value = mock_proc

        sampler = RamSampler(interval=0.05)
        sampler.start()
        time.sleep(0.06)
        sampler.stop()
        sampler.stop()  # Second stop should be safe


# ---------------------------------------------------------------------------
# VramTracker tests
# ---------------------------------------------------------------------------


def test_vram_tracker_no_cuda() -> None:
    """Assert peak_mb returns 0.0 when CUDA is unavailable."""
    with patch(
        "airllm_benchmark.services.metrics_sampler.torch.cuda.is_available",
        return_value=False,
    ):
        assert VramTracker.peak_mb() == 0.0
        VramTracker.reset()  # Should not raise


def test_vram_tracker_cuda_available() -> None:
    """Assert peak_mb returns correct value when CUDA is available."""
    with (
        patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.is_available",
            return_value=True,
        ),
        patch(
            "airllm_benchmark.services.metrics_sampler.torch.cuda.max_memory_allocated",
            return_value=256 * 1024 * 1024,
        ),
        patch("airllm_benchmark.services.metrics_sampler.torch.cuda.reset_peak_memory_stats"),
    ):
        VramTracker.reset()
        peak = VramTracker.peak_mb()
        assert peak == 256.0
