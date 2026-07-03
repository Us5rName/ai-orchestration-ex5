"""Tests for Metrics Timing PoC — timing returns valid elapsed time.

Run:
    uv run pytest tests/pocs/test_metrics_timing_poc.py -v
"""

from __future__ import annotations

from pocs.metrics_timing_poc import (
    TimingResult,
    poc_timing,
)


class TestPoCTiming:
    """Feature PoC: timing returns valid elapsed time."""

    def test_returns_timing_result(self) -> None:
        result = poc_timing()

        assert isinstance(result, TimingResult)

    def test_elapsed_is_positive(self) -> None:
        result = poc_timing()

        assert result.elapsed_seconds > 0

    def test_stop_after_start(self) -> None:
        result = poc_timing()

        assert result.stop_timestamp > result.start_timestamp

    def test_elapsed_matches_timestamps(self) -> None:
        result = poc_timing()

        expected = result.stop_timestamp - result.start_timestamp
        # elapsed uses perf_counter, timestamps use time.time() — allow
        # small drift but they should be in the same ballpark.
        assert abs(result.elapsed_seconds - expected) < 0.01
