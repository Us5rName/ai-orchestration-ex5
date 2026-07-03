"""Tests for Metrics Peak Calculation PoC — peak_calculation derives max from samples.

Run:
    uv run pytest tests/pocs/test_metrics_peak_poc.py -v
"""

from __future__ import annotations

from pocs.metrics_peak_poc import (
    PeakResult,
    poc_peak_calculation,
)
from pocs.metrics_sampling_poc import MemorySample


class TestPoCPeakCalculation:
    """Feature PoC: peak_calculation derives max from samples."""

    def test_returns_peak_result(self) -> None:
        samples = [
            MemorySample(timestamp=0.0, rss_mb=100.0),
            MemorySample(timestamp=0.1, rss_mb=200.0),
        ]
        result = poc_peak_calculation(samples)

        assert isinstance(result, PeakResult)

    def test_peak_is_maximum(self) -> None:
        samples = [
            MemorySample(timestamp=0.0, rss_mb=100.0),
            MemorySample(timestamp=0.1, rss_mb=250.0),
            MemorySample(timestamp=0.2, rss_mb=150.0),
        ]
        result = poc_peak_calculation(samples)

        assert result.peak_rss_mb == 250.0

    def test_sample_count_matches(self) -> None:
        samples = [
            MemorySample(timestamp=0.0, rss_mb=100.0),
            MemorySample(timestamp=0.1, rss_mb=200.0),
        ]
        result = poc_peak_calculation(samples)

        assert result.sample_count == 2

    def test_empty_samples_returns_zero(self) -> None:
        result = poc_peak_calculation([])

        assert result.peak_rss_mb == 0.0
        assert result.sample_count == 0
