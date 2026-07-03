"""Peak Calculation Feature PoC — Derive peak memory from samples.

Proves peak memory derivation works correctly before building
the full metrics module.

Run:
    uv run python pocs/metrics_peak_poc.py
"""

from __future__ import annotations

from dataclasses import dataclass

from pocs.metrics_sampling_poc import MemorySample


@dataclass
class PeakResult:
    """Result of peak memory calculation."""

    peak_rss_mb: float
    sample_count: int


def poc_peak_calculation(samples: list[MemorySample]) -> PeakResult:
    """Prove peak memory can be derived from a list of samples.

    Returns the maximum RSS value and the number of samples analysed.

    Args:
        samples: List of memory samples to analyse.

    Returns:
        PeakResult with peak RSS and sample count.
    """
    if not samples:
        return PeakResult(peak_rss_mb=0.0, sample_count=0)

    peak = max(s.rss_mb for s in samples)
    return PeakResult(peak_rss_mb=peak, sample_count=len(samples))


if __name__ == "__main__":
    samples = [
        MemorySample(timestamp=0.0, rss_mb=100.0),
        MemorySample(timestamp=0.1, rss_mb=250.0),
        MemorySample(timestamp=0.2, rss_mb=150.0),
    ]
    result = poc_peak_calculation(samples)
    print(f"Peak: {result.peak_rss_mb:.2f} MB ({result.sample_count} samples)")
