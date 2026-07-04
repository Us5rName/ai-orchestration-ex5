"""CPU Runner Benchmark PoC.

Runs CpuRunner with a real TransformersProvider against a small model.
Exercises the actual library with real hardware to confirm the runner
works end-to-end with accurate RAM measurements.

    uv run pytest tests/pocs/test_cpu_runner_benchmark_poc.py -v -s
"""

from __future__ import annotations

from airllm_benchmark.providers.transformers_provider import TransformersProvider
from airllm_benchmark.sdk.cpu_runner import CpuRunner

# Small model that runs quickly on CPU for benchmarking.
POC_MODEL = "meta-llama/Llama-3.2-1B"
POC_PROMPT = "What is 2+2?"
POC_MAX_TOKENS = 3


def _assert_common(record, quantization: str = "none") -> None:
    """Assert all MetricsRecord fields for a CPU run."""
    assert record.status == "success", f"Run failed: {record.error}"
    assert record.model == POC_MODEL
    assert record.mode == "cpu_baseline"
    assert record.provider == "transformers"
    assert record.prompt == POC_PROMPT
    assert record.prompt_id == "", "CPU runner passes empty prompt_id"
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
    # VRAM may be non-zero if quantization libs (e.g. bitsandbytes) touch GPU.


def _print_record(record) -> None:
    """Print a formatted benchmark summary."""
    print("\n===== CPU Runner Benchmark PoC =====")
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
    print(f"Status:         {record.status}")
    print(f"Timestamp:      {record.timestamp}")
    print("=====================================\n")


def test_cpu_runner_benchmark() -> None:
    """Run CpuRunner with real TransformersProvider and assert metrics."""
    provider = TransformersProvider(device="cpu", quantization="none")
    runner = CpuRunner()

    record = runner.run(
        provider=provider,
        model_id=POC_MODEL,
        prompt=POC_PROMPT,
        max_tokens=POC_MAX_TOKENS,
        quantization="none",
    )

    _assert_common(record, quantization="none")

    _print_record(record)


def test_cpu_runner_quantized_4bit() -> None:
    """Run CpuRunner with 4-bit quantization and assert metrics."""
    provider = TransformersProvider(device="cpu", quantization="4bit")
    runner = CpuRunner()

    record = runner.run(
        provider=provider,
        model_id=POC_MODEL,
        prompt=POC_PROMPT,
        max_tokens=POC_MAX_TOKENS,
        quantization="4bit",
    )

    _assert_common(record, quantization="4bit")

    _print_record(record)
