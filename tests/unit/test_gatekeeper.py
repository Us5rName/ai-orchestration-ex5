"""Tests for shared/gatekeeper.py — rate-limited external calls.

Covers: RateLimiter timing (no real sleeping — time is mocked), config
loading (missing file disables limiting), and call_with_rate_limit
propagating both return values and exceptions unchanged.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from airllm_benchmark.shared import gatekeeper
from airllm_benchmark.shared.gatekeeper import RateLimiter, call_with_rate_limit


@pytest.fixture(autouse=True)
def _fresh_limiter_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate the module-level limiter cache between tests."""
    monkeypatch.setattr(gatekeeper, "_LIMITERS", {})


class TestRateLimiter:
    """Tests for RateLimiter.acquire()."""

    def test_disabled_when_non_positive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """calls_per_minute <= 0 disables limiting — never sleeps."""
        sleep_calls: list[float] = []
        monkeypatch.setattr(gatekeeper.time, "sleep", sleep_calls.append)

        limiter = RateLimiter(calls_per_minute=0)
        limiter.acquire()
        limiter.acquire()

        assert sleep_calls == []

    def test_first_call_never_waits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The first acquire() has no prior call to wait on."""
        sleep_calls: list[float] = []
        monkeypatch.setattr(gatekeeper.time, "sleep", sleep_calls.append)
        monkeypatch.setattr(gatekeeper.time, "monotonic", lambda: 100.0)

        RateLimiter(calls_per_minute=60).acquire()

        assert sleep_calls == []

    def test_second_call_waits_remaining_interval(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A call within the interval sleeps for the remaining time."""
        sleep_calls: list[float] = []
        monkeypatch.setattr(gatekeeper.time, "sleep", sleep_calls.append)
        # Each acquire() reads the clock twice: once for `now`, once to
        # stamp `_last_call`. Two acquire() calls need four values.
        clock = iter([100.0, 100.0, 100.2, 100.2])
        monkeypatch.setattr(gatekeeper.time, "monotonic", lambda: next(clock))

        limiter = RateLimiter(calls_per_minute=60)  # 1s interval
        limiter.acquire()  # now=100.0, last_call set to 100.0
        limiter.acquire()  # now=100.2, waits 0.8s

        assert sleep_calls == pytest.approx([0.8])

    def test_call_after_interval_elapsed_does_not_wait(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A call after the interval has fully elapsed does not sleep."""
        sleep_calls: list[float] = []
        monkeypatch.setattr(gatekeeper.time, "sleep", sleep_calls.append)
        clock = iter([100.0, 100.0, 105.0, 105.0])
        monkeypatch.setattr(gatekeeper.time, "monotonic", lambda: next(clock))

        limiter = RateLimiter(calls_per_minute=60)  # 1s interval
        limiter.acquire()
        limiter.acquire()

        assert sleep_calls == []


class TestLoadLimits:
    """Tests for _load_limits()."""

    def test_missing_file_returns_empty(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(gatekeeper, "CONFIG_PATH", tmp_path / "missing.json")
        assert gatekeeper._load_limits() == {}

    def test_reads_configured_limits(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cfg_path = tmp_path / "rate_limits.json"
        cfg_path.write_text(json.dumps({"huggingface": {"calls_per_minute": 30}}))
        monkeypatch.setattr(gatekeeper, "CONFIG_PATH", cfg_path)

        assert gatekeeper._load_limits() == {"huggingface": {"calls_per_minute": 30}}


class TestCallWithRateLimit:
    """Tests for call_with_rate_limit()."""

    def test_returns_fn_result(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gatekeeper, "CONFIG_PATH", tmp_path / "missing.json")

        result = call_with_rate_limit("huggingface", lambda: "generated-text")

        assert result == "generated-text"

    def test_propagates_exceptions(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gatekeeper, "CONFIG_PATH", tmp_path / "missing.json")

        def _boom() -> None:
            raise RuntimeError("HF Hub unreachable")

        with pytest.raises(RuntimeError, match="HF Hub unreachable"):
            call_with_rate_limit("huggingface", _boom)

    def test_reuses_limiter_across_calls(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Same service name reuses one RateLimiter instead of reloading config."""
        monkeypatch.setattr(gatekeeper, "CONFIG_PATH", tmp_path / "missing.json")

        call_with_rate_limit("huggingface", lambda: None)
        call_with_rate_limit("huggingface", lambda: None)

        assert len(gatekeeper._LIMITERS) == 1
