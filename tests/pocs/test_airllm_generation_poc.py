"""Feature PoC for AirLLM generation — real model text generation.

Proves that the airllm_generator.generate_text() function can
tokenize a prompt, run generation on CUDA, and decode output
using an AirLLM model's built-in tokenizer.

Per docs/IMPLEMENTATION.md Step 2 — Feature PoCs.
Always test against real data.

    uv run pytest tests/pocs/test_airllm_generation_poc.py -v -s
"""

from __future__ import annotations


def test_generate_text_returns_valid_output() -> None:
    """generate_text() produces non-empty text and correct token count."""
    from airllm_benchmark.sdk.airllm_generator import generate_text
    from airllm_benchmark.sdk.airllm_loader import load_model

    model = load_model("Qwen/Qwen2.5-0.5B-Instruct", "4bit")

    prompt = "What is the capital of France?"
    max_tokens = 8

    output, tokens = generate_text(model, prompt, max_tokens)

    assert isinstance(output, str), "Output must be a string"
    assert len(output) > 0, "Output must not be empty"
    assert tokens > 0, "Token count must be positive"
    assert tokens <= max_tokens, f"Token count ({tokens}) exceeds max ({max_tokens})"

    print("\n===== Generation PoC =====")
    print(f"Prompt:  {prompt}")
    print(f"Output:  {output[:80]}...")
    print(f"Tokens:  {tokens}")
    print("==========================\n")


def test_generate_text_with_no_quantization() -> None:
    """generate_text() works with uncompressed model (none quantization)."""
    from airllm_benchmark.sdk.airllm_generator import generate_text
    from airllm_benchmark.sdk.airllm_loader import load_model

    model = load_model("Qwen/Qwen2.5-0.5B-Instruct", "none")

    prompt = "Count to three:"
    max_tokens = 8

    output, tokens = generate_text(model, prompt, max_tokens)

    assert isinstance(output, str), "Output must be a string"
    assert len(output) > 0, "Output must not be empty"
    assert tokens > 0, "Token count must be positive"

    print("\n===== Generation PoC (no quant) =====")
    print(f"Prompt:  {prompt}")
    print(f"Output:  {output[:80]}...")
    print(f"Tokens:  {tokens}")
    print("======================================\n")
