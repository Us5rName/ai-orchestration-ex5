"""API Gatekeeper — rate-limited access to external services.

All external calls (HuggingFace Hub downloads, provider HTTP calls) must
flow through here per CLAUDE.md §3. The benchmark runs single-threaded,
so calls are already issued in FIFO order; an overflow call simply blocks
in ``RateLimiter.acquire()`` until its slot is free rather than raising —
the benchmark must never crash due to rate limits.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "config" / "rate_limits.json"


class RateLimiter:
    """Rate limiter enforcing a fixed calls-per-minute ceiling."""

    def __init__(self, calls_per_minute: int) -> None:
        """Set the ceiling; a non-positive value disables limiting."""
        self._interval = 60.0 / calls_per_minute if calls_per_minute > 0 else 0.0
        self._last_call: float | None = None

    def acquire(self) -> None:
        """Block just long enough to respect the configured rate."""
        if self._interval <= 0:
            return
        now = time.monotonic()
        if self._last_call is not None:
            wait = self._last_call + self._interval - now
            if wait > 0:
                time.sleep(wait)
        self._last_call = time.monotonic()


def _load_limits() -> dict[str, dict[str, int]]:
    """Read config/rate_limits.json; an absent file means no limiting."""
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


_LIMITERS: dict[str, RateLimiter] = {}


def call_with_rate_limit[T](service: str, fn: Callable[[], T]) -> T:
    """Execute ``fn()`` through the named service's rate limiter.

    Args:
        service: Rate-limit bucket name (key in config/rate_limits.json).
        fn: Zero-argument callable to execute once the slot is free.

    Returns:
        Whatever ``fn()`` returns.

    Raises:
        Exception: Whatever ``fn()`` raises — the gatekeeper only paces
            calls, it never swallows errors from the wrapped call.
    """
    if service not in _LIMITERS:
        limits = _load_limits()
        _LIMITERS[service] = RateLimiter(limits.get(service, {}).get("calls_per_minute", 0))

    _LIMITERS[service].acquire()
    return fn()
