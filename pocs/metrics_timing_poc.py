"""Timing Feature PoC — Wall-clock timing with start/stop/elapsed.

Proves perf_counter-based timing works correctly before building
the full metrics module.

Run:
    uv run python pocs/metrics_timing_poc.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class TimingResult:
    """Result of a timed operation."""

    elapsed_seconds: float
    start_timestamp: float
    stop_timestamp: float


def poc_timing() -> TimingResult:
    """Prove wall-clock timing works with perf_counter.

    Returns start/stop timestamps and elapsed seconds.
    """
    start = time.perf_counter()
    start_ts = time.time()

    # Simulate work
    time.sleep(0.05)

    stop_ts = time.time()
    stop = time.perf_counter()

    return TimingResult(
        elapsed_seconds=stop - start,
        start_timestamp=start_ts,
        stop_timestamp=stop_ts,
    )


if __name__ == "__main__":
    result = poc_timing()
    print(f"Elapsed: {result.elapsed_seconds:.4f}s")
    print(f"Start: {result.start_timestamp}")
    print(f"Stop:  {result.stop_timestamp}")
