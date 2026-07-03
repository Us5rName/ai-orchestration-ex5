"""psutil Library PoC — Step 1 of IMPLEMENTATION.md.

Minimal proof that psutil is importable and can measure process memory
and elapsed time. This validates the external dependency before building
the metrics service.

Run:
    uv run python pocs/metrics_library_poc.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import psutil


@dataclass
class PoCMetrics:
    """Simple metrics record for PoC validation."""

    elapsed_seconds: float = 0.0
    peak_rss_mb: float = 0.0
    samples: int = 0


def measure_process() -> PoCMetrics:
    """Measure current process memory and simulate work timing.

    Returns:
        PoCMetrics with elapsed time and peak RSS memory usage.
    """
    process = psutil.Process()

    start = time.perf_counter()

    # Simulate work — allocate and release memory
    data = [0] * 1_000_000
    time.sleep(0.1)
    peak_rss = process.memory_info().rss / (1024 * 1024)
    del data

    elapsed = time.perf_counter() - start

    return PoCMetrics(
        elapsed_seconds=elapsed,
        peak_rss_mb=peak_rss,
        samples=1,
    )


if __name__ == "__main__":
    result = measure_process()
    print(f"Elapsed: {result.elapsed_seconds:.4f}s")
    print(f"Peak RSS: {result.peak_rss_mb:.2f} MB")
    print(f"Samples: {result.samples}")
