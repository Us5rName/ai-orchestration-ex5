"""GPU Runner Benchmark PoC.

Standalone proof-of-concept that runs GpuRunner with a real
TransformersProvider against a small model. Collects real timing
and memory metrics. Exercises the actual library with real
hardware — the point is to confirm the runner works end-to-end.

Run with:
    uv run pytest tests/pocs/test_gpu_runner_benchmark_poc.py -v -s
"""

from __future__ import annotations

import pytest

from airllm_benchmark.providers.transformers_provider import TransformersProvider
from airllm_benchmark.sdk.gpu_runner import GpuRunner

# Small model that fits in VRAM for quick benchmarking.
POC_MODEL = "meta-llama/Llama-3.2-1B"
POC_PROMPT = "What is 2+2?"
POC_MAX_TOKENS = 16


def _has_cuda() -> bool:
    """Check if CUDA is available on this machine."""
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


@pytest.mark.skipif(
    not _has_cuda(),
    reason="CUDA not available — PoC requires GPU hardware",
)
def test_gpu_runner_benchmark() -> None:
    """Run GpuRunner with real TransformersProvider and assert valid output.

    This PoC proves:
    - GpuRunner can delegate to a real provider
    - MetricsCollector captures real timing/memory
    - The runner returns a valid MetricsRecord with success status
    """
    provider = TransformersProvider(device="cuda")
    runner = GpuRunner()

    record = runner.run(
        provider=provider,
        model_id=POC_MODEL,
        prompt=POC_PROMPT,
        max_tokens=POC_MAX_TOKENS,
    )

    # Assert the runner returned a valid record
    assert record.status == "success", f"Run failed: {record.error}"
    assert record.model == POC_MODEL
    assert record.mode == "gpu_provider"
    assert record.prompt == POC_PROMPT
    assert record.max_new_tokens == POC_MAX_TOKENS
    assert record.load_time_s > 0, "Load time should be positive"
    assert record.total_runtime_s > 0, "Total runtime should be positive"
    assert record.tokens_generated > 0, "Should have generated tokens"
    assert record.peak_ram_mb > 0, "RAM usage should be measurable"

    # Print benchmark results for human verification
    print("\n===== GPU Runner Benchmark PoC =====")
    print(f"Model:          {record.model}")
    print(f"Mode:           {record.mode}")
    print(f"Provider:       {record.provider}")
    print(f"Load time:      {record.load_time_s:.2f}s")
    print(f"Total runtime:  {record.total_runtime_s:.2f}s")
    print(f"Tokens gen:     {record.tokens_generated}")
    print(f"Peak RAM:       {record.peak_ram_mb:.1f} MB")
    print(f"Peak VRAM:      {record.peak_vram_mb:.1f} MB")
    print(f"Status:         {record.status}")
    print("=====================================\n")


@pytest.mark.skipif(
    _has_cuda(),
    reason="CUDA available — running CPU fallback PoC instead",
)
def test_gpu_runner_cpu_fallback() -> None:
    """Fallback PoC: run on CPU when CUDA is unavailable.

    Proves the runner works even without GPU — delegates to
    provider on CPU device and collects metrics correctly.
    """
    provider = TransformersProvider(device="cpu")
    runner = GpuRunner()

    record = runner.run(
        provider=provider,
        model_id=POC_MODEL,
        prompt=POC_PROMPT,
        max_tokens=POC_MAX_TOKENS,
    )

    assert record.status == "success", f"Run failed: {record.error}"
    assert record.model == POC_MODEL
    assert record.load_time_s > 0
    assert record.total_runtime_s > 0
    assert record.tokens_generated > 0

    print("\n===== GPU Runner Benchmark PoC (CPU fallback) =====")
    print(f"Model:          {record.model}")
    print(f"Mode:           {record.mode}")
    print(f"Provider:       {record.provider}")
    print(f"Load time:      {record.load_time_s:.2f}s")
    print(f"Total runtime:  {record.total_runtime_s:.2f}s")
    print(f"Tokens gen:     {record.tokens_generated}")
    print(f"Peak RAM:       {record.peak_ram_mb:.1f} MB")
    print(f"Status:         {record.status}")
    print("=================================================\n")
