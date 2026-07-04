"""Tests for sdk/cpu_runner.py — CpuRunner protocol compliance.

Verifies the runner class exists and implements the InferenceRunner
protocol with a callable run() method.
"""

from __future__ import annotations

from airllm_benchmark.sdk.cpu_runner import CpuRunner


class TestCpuRunnerProtocol:
    """Verify CpuRunner implements InferenceRunner protocol."""

    def test_runner_exists(self) -> None:
        """CpuRunner class can be imported and instantiated."""
        runner = CpuRunner()
        assert runner is not None

    def test_runner_has_run_method(self) -> None:
        """CpuRunner exposes run() method per protocol."""
        runner = CpuRunner()
        assert hasattr(runner, "run")
        assert callable(runner.run)
