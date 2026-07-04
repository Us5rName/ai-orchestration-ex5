"""Module PoC for AirllmRunner — end-to-end usage via the module.

Uses the actual AirllmRunner + helpers to load a real model and
generate text. Follows testing-airllm.py pattern exactly, with
reduced max_new_tokens to keep the test fast.

Per docs/IMPLEMENTATION.md Step 3 — Full Module PoC.
"""

from __future__ import annotations

import pytest

from tests.pocs._cuda import has_cuda


@pytest.mark.skipif(not has_cuda(), reason="CUDA not available — PoC requires GPU hardware")
def test_airllm_runner_module_poc() -> None:
    """Run AirllmRunner with real model and verify metrics output.

    Follows testing-airllm.py pattern:
    - Qwen/Qwen2.5-7B-Instruct with 4bit compression
    - Same prompt from reference
    - Reduced max_new_tokens (4 instead of 20) for speed
    """
    from airllm_benchmark.sdk.airllm_runner import AirllmRunner

    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    prompt = "What is the capital of United States?"
    quant = "4bit"
    max_tokens = 4

    runner = AirllmRunner()
    record = runner.run(
        provider=None,
        model_id=model_name,
        prompt=prompt,
        max_tokens=max_tokens,
        quantization=quant,
    )

    # Verify metrics record structure
    assert record.status == "success", f"Expected success, got: {record.status}"
    assert record.tokens_generated > 0, "Expected tokens to be generated"
    assert record.mode == "airllm", "Mode must be airllm"
    assert record.provider == "airllm", "Provider must be airllm"
    assert record.quantization == "4bit", "Quantization must be 4bit"
    assert record.total_runtime_s > 0, "Runtime must be positive"
    assert record.load_time_s > 0, "Load time must be positive"
    assert record.peak_ram_mb > 0, "RAM usage must be recorded"
