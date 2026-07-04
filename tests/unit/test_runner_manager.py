"""RunnerManager dispatch tests.

Verifies that RunnerManager correctly routes mode strings to
the appropriate runner instances and caches them.
"""

from __future__ import annotations

import pytest

from airllm_benchmark.sdk.airllm_runner import AirllmRunner
from airllm_benchmark.sdk.cpu_runner import CpuRunner
from airllm_benchmark.sdk.gpu_runner import GpuRunner
from airllm_benchmark.sdk.runner import RunnerManager


class TestRunnerManagerDispatch:
    """RunnerManager routes to correct runner instances."""

    def test_dispatch_gpu_runner(self) -> None:
        """get_runner('gpu_provider') returns GpuRunner instance."""
        mgr = RunnerManager()
        assert isinstance(mgr.get_runner("gpu_provider"), GpuRunner)

    def test_dispatch_cpu_runner(self) -> None:
        """get_runner('cpu_baseline') returns CpuRunner instance."""
        mgr = RunnerManager()
        assert isinstance(mgr.get_runner("cpu_baseline"), CpuRunner)

    def test_dispatch_airllm_runner(self) -> None:
        """get_runner('airllm') returns AirllmRunner instance."""
        mgr = RunnerManager()
        assert isinstance(mgr.get_runner("airllm"), AirllmRunner)

    def test_dispatch_caches_instances(self) -> None:
        """Repeated calls return same runner instance."""
        mgr = RunnerManager()
        assert mgr.get_runner("gpu_provider") is mgr.get_runner("gpu_provider")
        assert mgr.get_runner("cpu_baseline") is mgr.get_runner("cpu_baseline")
        assert mgr.get_runner("airllm") is mgr.get_runner("airllm")

    def test_dispatch_invalid_mode_raises(self) -> None:
        """Unknown mode raises ValueError."""
        with pytest.raises(ValueError, match="Unknown"):
            RunnerManager().get_runner("invalid")
