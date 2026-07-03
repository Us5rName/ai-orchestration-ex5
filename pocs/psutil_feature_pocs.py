"""Feature PoCs — psutil memory sampling and peak calculation.

Proves each MetricsCollector feature can be implemented with psutil:
1. Continuous memory sampling at 1-second intervals (background thread)
2. Peak RAM extraction from collected samples
"""

from __future__ import annotations

import threading
import time
from typing import Any

import psutil


class MemorySampler:
    """Background sampler that records RSS at fixed intervals."""

    def __init__(self, interval: float = 1.0) -> None:
        """Initialise sampler.

        Args:
            interval: Seconds between samples.
        """
        self._interval = interval
        self._samples: list[float] = []
        self._running = False
        self._thread: threading.Thread | None = None

    # --- Public API matching MetricsCollector interface ---

    def start(self) -> None:
        """Begin background memory sampling."""
        self._samples.clear()
        self._running = True
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop background sampling and wait for thread."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def peak_ram_mb(self) -> float:
        """Return peak RSS in megabytes from all collected samples."""
        if not self._samples:
            return 0.0
        return max(self._samples)

    # --- Internal ---

    def _sample_loop(self) -> None:
        """Run sampling loop until stopped."""
        while self._running:
            rss_bytes = _get_current_rss()
            self._samples.append(rss_bytes / (1024 * 1024))
            time.sleep(self._interval)


def _get_current_rss() -> int:
    """Return current process RSS in bytes."""
    return psutil.Process().memory_info().rss


def _allocate_memory(size_mb: float, duration: float = 2.0) -> Any:
    """Allocate memory temporarily so the sampler can observe it.

    Args:
        size_mb: Megabytes to allocate.
        duration: How long to hold the allocation.

    Returns:
        The allocated buffer (caller discards to free).
    """

    def _hold() -> None:
        time.sleep(duration)

    thread = threading.Thread(target=_hold, daemon=True)
    thread.start()
    # Allocate and return — caller deletes to free
    return bytearray(int(size_mb * 1024 * 1024))


__all__ = ["MemorySampler", "_allocate_memory"]
