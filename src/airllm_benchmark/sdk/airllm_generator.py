"""AirLLM generation helpers.

Tokenizes input, runs generation, and decodes output using the
AirLLM model's built-in tokenizer. Follows testing-airllm.py pattern.

Per docs/TODO.md task 5.4 and testing-airllm.py reference.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from airllm import AutoModel


def generate_text(
    model: AutoModel,
    prompt: str,
    max_tokens: int,
    max_length: int = 128,
) -> tuple[str, int]:
    """Generate text from a prompt using an AirLLM model.

    Tokenizes the prompt, runs generation on CUDA, and decodes
    the full output sequence. Returns the generated text and the
    number of new tokens produced.

    Args:
        model: Loaded AirLLM AutoModel instance.
        prompt: Input text to complete.
        max_tokens: Maximum new tokens to generate.
        max_length: Maximum input sequence length for tokenization.

    Returns:
        Tuple of (generated_text, tokens_generated).
    """
    # Tokenize input (matching testing-airllm.py pattern).
    input_tokens = model.tokenizer(
        [prompt],
        return_tensors="pt",
        return_attention_mask=False,
        truncation=True,
        max_length=max_length,
        padding=False,
    )

    # Generate on CUDA with KV cache for faster decoding.
    generation_output = model.generate(
        input_tokens["input_ids"].cuda(),
        max_new_tokens=max_tokens,
        use_cache=True,
        return_dict_in_generate=True,
    )

    # Decode full output (prompt + generated text).
    output = model.tokenizer.decode(generation_output.sequences[0])

    # Count only the newly generated tokens.
    input_len = input_tokens["input_ids"].shape[1]
    tokens_generated = generation_output.sequences.shape[1] - input_len

    return output, int(tokens_generated)
