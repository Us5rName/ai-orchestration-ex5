"""Tests for sdk/gpu_runner.py — GpuRunner protocol compliance.

Verifies the runner class exists and implements the InferenceRunner
protocol with a callable run() method.
"""

from __future__ import annotations

from airllm_benchmark.sdk.gpu_runner import GpuRunner


class TestGpuRunnerProtocol:
    """Verify GpuRunner implements InferenceRunner protocol."""

    def test_runner_exists(self) -> None:
        """GpuRunner class can be imported and instantiated."""
        runner = GpuRunner()
        assert runner is not None

    def test_runner_has_run_method(self) -> None:
        """GpuRunner exposes run() method per protocol."""
        runner = GpuRunner()
        assert hasattr(runner, "run")
        assert callable(runner.run)
