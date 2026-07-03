"""Internal sampler utilities for MetricsCollector.

Background RAM sampling and CUDA VRAM tracking.
Not part of the public API — imported by services/metrics.py only.
"""

from __future__ import annotations

import threading
import time

import psutil
import torch


class RamSampler:
    """Background thread that samples process RSS at fixed intervals."""

    def __init__(self, interval: float = 1.0) -> None:
        """Init sampler.

        Args:
            interval: Seconds between samples.
        """
        self._interval = interval
        self._samples: list[float] = []
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Begin background RAM sampling."""
        with self._lock:
            self._samples.clear()
            self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop sampling and wait for thread."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def peak_mb(self) -> float:
        """Return peak RSS across all samples in megabytes."""
        with self._lock:
            return max(self._samples) if self._samples else 0.0

    def _loop(self) -> None:
        """Record RSS each interval until stopped."""
        while self._running:
            rss = psutil.Process().memory_info().rss / (1024 * 1024)
            with self._lock:
                self._samples.append(rss)
            time.sleep(self._interval)


class VramTracker:
    """Wraps torch.cuda peak memory tracking."""

    @staticmethod
    def reset() -> None:
        """Reset CUDA peak stats. No-op if CUDA unavailable."""
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()

    @staticmethod
    def peak_mb() -> float:
        """Return peak CUDA allocation in MB. 0.0 if unavailable."""
        if not torch.cuda.is_available():
            return 0.0
        return torch.cuda.max_memory_allocated() / (1024 * 1024)
