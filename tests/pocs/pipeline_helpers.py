"""Pipeline PoC helpers.

Reusable building blocks for runner pipeline proof-of-concepts.
Provides a mock provider and MetricsRecord assertion utilities.

Per modular-design: Single Responsibility — test infrastructure
separated from test execution.
"""

from __future__ import annotations

from airllm_benchmark.services.metrics import MetricsRecord

# ——— Mock Provider ———


class MockProvider:
    """In-memory InferenceProvider for pipeline PoC.

    Input:  model_id, device, prompt, max_tokens
    Output: deterministic (text, token_count) tuple
    Setup:  no configuration needed

    Returns deterministic output so assertions are reproducible.
    Exercises the real runner code path (timing, metrics, errors).
    """

    def load_model(self, model_id: str, device: str) -> None:
        """No-op load — model is already in memory."""

    def generate(self, prompt: str, max_tokens: int) -> tuple[str, int]:
        """Return synthetic generation with known token count."""
        return f"Generated response to: {prompt}", 10

    def unload(self) -> None:
        """No-op unload — no resources to release."""


# ——— Assertion Helpers ———


def assert_record_structure(record: MetricsRecord, expected_mode: str) -> None:
    """Verify MetricsRecord has all 18 fields with correct types and values.

    Asserts the output dict structure matches INTERFACES.md §4 exactly.

    Input:  MetricsRecord instance, expected mode string
    Output: raises AssertionError on any field mismatch
    """
    # Identity fields — set by runner context
    assert isinstance(record.run_id, str) and record.run_id.startswith("run_")
    assert record.model == "mock/tiny-model"
    assert record.mode == expected_mode
    assert record.provider in ("mock", "airllm")
    assert record.prompt == "What is 2+2?"
    assert record.prompt_id == ""
    assert record.quantization == "none"
    assert record.max_new_tokens == 16

    # Timing fields — measured by MetricsCollector
    assert isinstance(record.load_time_s, float) and record.load_time_s >= 0
    assert isinstance(record.ttft_s, float) and record.ttft_s >= 0
    assert isinstance(record.total_runtime_s, float) and record.total_runtime_s > 0

    # Generation fields — from provider output
    assert record.tokens_generated == 10
    assert isinstance(record.generation_throughput, float)
    assert record.generation_throughput > 0

    # Memory fields — from psutil sampler
    assert isinstance(record.peak_ram_mb, float) and record.peak_ram_mb > 0
    assert isinstance(record.peak_vram_mb, float) and record.peak_vram_mb >= 0

    # Status fields
    assert record.status == "success"
    assert record.error == ""
    assert isinstance(record.timestamp, str) and len(record.timestamp) > 0


def print_record(record: MetricsRecord) -> None:
    """Print a formatted pipeline summary for visibility."""
    print(f"\n--- {record.mode} ({record.provider}) ---")
    print(f"  Run ID:     {record.run_id}")
    print(f"  Model:      {record.model}")
    print(f"  Load:       {record.load_time_s:.4f}s")
    print(f"  TTFT:       {record.ttft_s:.4f}s")
    print(f"  Runtime:    {record.total_runtime_s:.4f}s")
    print(f"  Tokens:     {record.tokens_generated}")
    print(f"  Throughput: {record.generation_throughput:.2f} tok/s")
    print(f"  Peak RAM:   {record.peak_ram_mb:.1f} MB")
    print(f"  Status:     {record.status}")
    print("-------------------------------")
