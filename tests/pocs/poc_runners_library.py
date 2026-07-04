"""Library PoC for test_runners.py cross-runner testing.

Verifies all three runner classes can be imported and instantiated
without side effects, and that the RunnerManager can dispatch to
real runner instances.
"""

from __future__ import annotations

from airllm_benchmark.sdk.airllm_runner import AirllmRunner
from airllm_benchmark.sdk.cpu_runner import CpuRunner
from airllm_benchmark.sdk.gpu_runner import GpuRunner
from airllm_benchmark.sdk.runner import RunnerManager


def main() -> None:
    """Run PoC and print results."""
    # Verify all runners are importable and instantiable
    gpu = GpuRunner()
    cpu = CpuRunner()
    airllm = AirllmRunner()

    assert gpu is not None, "GpuRunner instantiation failed"
    assert cpu is not None, "CpuRunner instantiation failed"
    assert airllm is not None, "AirllmRunner instantiation failed"
    print("[OK] All three runners instantiated successfully")

    # Verify all runners have callable run() method
    assert callable(gpu.run), "GpuRunner.run not callable"
    assert callable(cpu.run), "CpuRunner.run not callable"
    assert callable(airllm.run), "AirllmRunner.run not callable"
    print("[OK] All runners expose callable run() method")

    # Verify RunnerManager dispatches to real runner classes
    mgr = RunnerManager()
    r_gpu = mgr.get_runner("gpu_provider")
    r_cpu = mgr.get_runner("cpu_baseline")
    r_airllm = mgr.get_runner("airllm")

    assert isinstance(r_gpu, GpuRunner), "Manager returned wrong GPU runner type"
    assert isinstance(r_cpu, CpuRunner), "Manager returned wrong CPU runner type"
    assert isinstance(r_airllm, AirllmRunner), "Manager returned wrong AirLLM runner type"
    print("[OK] RunnerManager dispatches to correct runner types")

    # Verify RunnerManager caching
    assert mgr.get_runner("gpu_provider") is r_gpu, "GPU runner not cached"
    assert mgr.get_runner("cpu_baseline") is r_cpu, "CPU runner not cached"
    assert mgr.get_runner("airllm") is r_airllm, "AirLLM runner not cached"
    print("[OK] RunnerManager caches runner instances")

    print("\nAll PoC assertions passed.")


if __name__ == "__main__":
    main()
