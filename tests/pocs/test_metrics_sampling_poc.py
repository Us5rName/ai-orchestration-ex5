"""Tests for Metrics Sampling PoC — memory_sampling collects samples.

Run:
    uv run pytest tests/pocs/test_metrics_sampling_poc.py -v
"""

from __future__ import annotations

from pocs.metrics_sampling_poc import (
    MemorySample,
    SamplingResult,
    poc_memory_sampling,
)


class TestPoCMemorySampling:
    """Feature PoC: memory_sampling collects samples."""

    def test_returns_sampling_result(self) -> None:
        result = poc_memory_sampling(duration=0.2, interval=0.05)

        assert isinstance(result, SamplingResult)

    def test_collects_samples(self) -> None:
        result = poc_memory_sampling(duration=0.2, interval=0.05)

        assert len(result.samples) >= 2

    def test_samples_have_positive_rss(self) -> None:
        result = poc_memory_sampling(duration=0.1, interval=0.05)

        for sample in result.samples:
            assert isinstance(sample, MemorySample)
            assert sample.rss_mb > 0

    def test_duration_is_positive(self) -> None:
        result = poc_memory_sampling(duration=0.1, interval=0.05)

        assert result.duration_seconds > 0
