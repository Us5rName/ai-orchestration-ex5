"""Tests for psutil Library PoC — Step 1 of IMPLEMENTATION.md.

Verifies psutil is importable and can measure process memory and timing.
No external model downloads required — tests run against the current process.

Run:
    uv run pytest tests/pocs/test_metrics_library_poc.py -v
"""

from __future__ import annotations

from pocs.metrics_library_poc import PoCMetrics, measure_process


class TestMetricsLibraryPoC:
    """Tests for psutil library PoC."""

    def test_measure_returns_metrics(self) -> None:
        """Assert PoC produces a valid PoCMetrics instance."""
        result = measure_process()

        assert isinstance(result, PoCMetrics)

    def test_elapsed_is_positive(self) -> None:
        """Assert measured elapsed time is greater than zero."""
        result = measure_process()

        assert result.elapsed_seconds > 0

    def test_peak_rss_is_positive(self) -> None:
        """Assert peak RSS memory measurement is greater than zero."""
        result = measure_process()

        assert result.peak_rss_mb > 0

    def test_samples_counted(self) -> None:
        """Assert samples are counted."""
        result = measure_process()

        assert result.samples >= 1
