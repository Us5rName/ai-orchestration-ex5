"""GPU Runner Benchmark PoC.

Runs GpuRunner with a real TransformersProvider against a small model.
Exercises the actual library with real hardware to confirm the runner
works end-to-end with accurate measurements.

    uv run pytest tests/pocs/test_gpu_runner_benchmark_poc.py -v -s
"""

from __future__ import annotations

import pytest

from airllm_benchmark.providers.transformers_provider import TransformersProvider
from airllm_benchmark.sdk.gpu_runner import GpuRunner

# Small model that fits in VRAM for quick benchmarking.
POC_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
POC_PROMPT = "What is 2+2?"
POC_MAX_TOKENS = 16


def _has_cuda() -> bool:
    """Check if CUDA is available on this machine."""
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


def _assert_common(
    record,
    *,
    expect_vram: bool = False,
    quantization: str = "none",
) -> None:
    """Assert all 18 MetricsRecord fields across GPU and CPU runs."""
    assert record.status == "success", f"Run failed: {record.error}"
    assert record.model == POC_MODEL
    assert record.mode == "gpu_provider"
    assert record.provider == "transformers"
    assert record.prompt == POC_PROMPT
    assert record.prompt_id == "", "GPU runner passes empty prompt_id"
    assert record.quantization == quantization
    assert record.max_new_tokens == POC_MAX_TOKENS
    assert record.run_id.startswith("run_"), "Run ID should be prefixed"
    assert record.timestamp, "Timestamp should be set"
    assert record.error == "", "Error should be empty on success"

    assert record.load_time_s > 0, "Load time should be positive"
    assert record.ttft_s > 0, "TTFT should be positive"
    assert record.total_runtime_s > 0, "Total runtime should be positive"
    assert record.ttft_s >= record.load_time_s, "TTFT >= load_time"
    assert record.total_runtime_s >= record.ttft_s, "Runtime >= TTFT"

    assert record.tokens_generated > 0, "Should have generated tokens"
    assert record.generation_throughput > 0, "Throughput must be positive"

    assert record.peak_ram_mb > 0, "RAM usage should be measurable"
    if expect_vram:
        assert record.peak_vram_mb > 0, "VRAM should be measurable on GPU"


def _print_record(record) -> None:
    """Print a formatted benchmark summary."""
    print("\n===== GPU Runner Benchmark PoC =====")
    print(f"Run ID:         {record.run_id}")
    print(f"Model:          {record.model}")
    print(f"Mode:           {record.mode}")
    print(f"Provider:       {record.provider}")
    print(f"Quantization:   {record.quantization}")
    print(f"Max tokens:     {record.max_new_tokens}")
    print(f"Load time:      {record.load_time_s:.2f}s")
    print(f"TTFT:           {record.ttft_s:.2f}s")
    print(f"Total runtime:  {record.total_runtime_s:.2f}s")
    print(f"Tokens gen:     {record.tokens_generated}")
    print(f"Throughput:     {record.generation_throughput:.2f} tok/s")
    print(f"Peak RAM:       {record.peak_ram_mb:.1f} MB")
    print(f"Peak VRAM:      {record.peak_vram_mb:.1f} MB")
    print(f"Status:         {record.status}")
    print(f"Timestamp:      {record.timestamp}")
    print("=====================================\n")


@pytest.mark.skipif(
    not _has_cuda(),
    reason="CUDA not available — PoC requires GPU hardware",
)
def test_gpu_runner_benchmark() -> None:
    """Run GpuRunner with real TransformersProvider and assert all metrics."""
    provider = TransformersProvider(device="cuda", quantization="none")
    runner = GpuRunner()

    record = runner.run(
        provider=provider,
        model_id=POC_MODEL,
        prompt=POC_PROMPT,
        max_tokens=POC_MAX_TOKENS,
        quantization="none",
    )

    _assert_common(record, expect_vram=True, quantization="none")

    _print_record(record)


@pytest.mark.skipif(
    not _has_cuda(),
    reason="CUDA not available — PoC requires GPU hardware",
)
def test_gpu_runner_quantized_4bit() -> None:
    """Run GpuRunner with 4-bit quantization and assert all metrics."""
    provider = TransformersProvider(device="cuda", quantization="4bit")
    runner = GpuRunner()

    record = runner.run(
        provider=provider,
        model_id=POC_MODEL,
        prompt=POC_PROMPT,
        max_tokens=POC_MAX_TOKENS,
        quantization="4bit",
    )

    _assert_common(record, expect_vram=True, quantization="4bit")

    _print_record(record)


@pytest.mark.skipif(
    _has_cuda(),
    reason="CUDA available — running GPU PoC instead",
)
def test_gpu_runner_cpu_fallback() -> None:
    """Fallback PoC: run on CPU when CUDA is unavailable."""
    provider = TransformersProvider(device="cpu", quantization="none")
    runner = GpuRunner()

    record = runner.run(
        provider=provider,
        model_id=POC_MODEL,
        prompt=POC_PROMPT,
        max_tokens=POC_MAX_TOKENS,
        quantization="none",
    )

    _assert_common(record, expect_vram=False, quantization="none")

    _print_record(record)
