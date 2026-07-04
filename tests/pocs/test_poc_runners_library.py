"""Test for runners library PoC.

Verifies all three runner classes are importable, instantiable,
and dispatchable via RunnerManager.
"""

from __future__ import annotations

from airllm_benchmark.sdk.airllm_runner import AirllmRunner
from airllm_benchmark.sdk.cpu_runner import CpuRunner
from airllm_benchmark.sdk.gpu_runner import GpuRunner
from airllm_benchmark.sdk.runner import RunnerManager


def test_all_runners_instantiable() -> None:
    """All three runner classes can be instantiated."""
    gpu = GpuRunner()
    cpu = CpuRunner()
    airllm = AirllmRunner()

    assert gpu is not None
    assert cpu is not None
    assert airllm is not None


def test_all_runners_expose_run_method() -> None:
    """All runners expose callable run() method."""
    assert callable(GpuRunner().run)
    assert callable(CpuRunner().run)
    assert callable(AirllmRunner().run)


def test_runner_manager_dispatches_real_runners() -> None:
    """RunnerManager returns correct runner types for each mode."""
    mgr = RunnerManager()

    assert isinstance(mgr.get_runner("gpu_provider"), GpuRunner)
    assert isinstance(mgr.get_runner("cpu_baseline"), CpuRunner)
    assert isinstance(mgr.get_runner("airllm"), AirllmRunner)


def test_runner_manager_caches_instances() -> None:
    """RunnerManager returns same instance on repeated calls."""
    mgr = RunnerManager()

    gpu1 = mgr.get_runner("gpu_provider")
    gpu2 = mgr.get_runner("gpu_provider")
    assert gpu1 is gpu2

    cpu1 = mgr.get_runner("cpu_baseline")
    cpu2 = mgr.get_runner("cpu_baseline")
    assert cpu1 is cpu2

    air1 = mgr.get_runner("airllm")
    air2 = mgr.get_runner("airllm")
    assert air1 is air2
