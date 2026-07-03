"""Transformers Library PoC — Step 1 of IMPLEMENTATION.md.

Minimal proof that the HuggingFace `transformers` library is importable
and can load a tiny model + generate text. Uses a tiny GPT2 model to
avoid downloading large weights.

Run:
    uv run python pocs/transformers_library_poc.py
"""

from __future__ import annotations

from transformers import AutoModelForCausalLM, AutoTokenizer

# Tiny model for PoC — avoids downloading large weights.
TINY_MODEL = "hf-internal-testing/tiny-random-gpt2"


def load_and_generate(prompt: str = "Hello, world!") -> str:
    """Load a tiny model and generate text from a prompt.

    Args:
        prompt: Input text to complete.

    Returns:
        Generated text string.
    """
    tokenizer = AutoTokenizer.from_pretrained(TINY_MODEL)
    model = AutoModelForCausalLM.from_pretrained(TINY_MODEL)

    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=16)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return result


if __name__ == "__main__":
    text = load_and_generate()
    print(f"Generated: {text}")
