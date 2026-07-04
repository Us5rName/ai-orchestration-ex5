"""Tests for sdk/airllm_runner.py — AirllmRunner protocol compliance.

Verifies the runner class exists and implements the InferenceRunner
protocol with a callable run() method.
"""

from __future__ import annotations

from airllm_benchmark.sdk.airllm_runner import AirllmRunner


class TestAirllmRunnerProtocol:
    """Verify AirllmRunner implements InferenceRunner protocol."""

    def test_runner_exists(self) -> None:
        """AirllmRunner class can be imported and instantiated."""
        runner = AirllmRunner()
        assert runner is not None

    def test_runner_has_run_method(self) -> None:
        """AirllmRunner exposes run() method per protocol."""
        runner = AirllmRunner()
        assert hasattr(runner, "run")
        assert callable(runner.run)
