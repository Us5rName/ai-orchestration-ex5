"""Memory Sampling Feature PoC — Periodic RSS sampling at configurable interval.

Proves psutil-based memory sampling works correctly before building
the full metrics module.

Run:
    uv run python pocs/metrics_sampling_poc.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import psutil


@dataclass
class MemorySample:
    """Single memory sample from psutil."""

    timestamp: float
    rss_mb: float


@dataclass
class SamplingResult:
    """Result of periodic memory sampling."""

    samples: list[MemorySample] = field(default_factory=list)
    duration_seconds: float = 0.0


def poc_memory_sampling(
    duration: float = 0.5,
    interval: float = 0.1,
) -> SamplingResult:
    """Prove periodic RSS sampling works with psutil.

    Samples the current process memory at the given interval for the
    specified duration. Returns all collected samples.

    Args:
        duration: How long to sample (seconds).
        interval: Time between samples (seconds).

    Returns:
        SamplingResult with list of MemorySample entries.
    """
    process = psutil.Process()
    result = SamplingResult()

    start = time.perf_counter()
    while time.perf_counter() - start < duration:
        mem = process.memory_info()
        result.samples.append(
            MemorySample(
                timestamp=time.time(),
                rss_mb=mem.rss / (1024 * 1024),
            )
        )
        time.sleep(interval)

    result.duration_seconds = time.perf_counter() - start
    return result


if __name__ == "__main__":
    result = poc_memory_sampling(duration=0.3, interval=0.1)
    print(f"Samples: {len(result.samples)}, Duration: {result.duration_seconds:.2f}s")
    for s in result.samples:
        print(f"  {s.timestamp}: {s.rss_mb:.2f} MB")
