"""Library PoC for AirLLM — real model load + generation.

Verifies that airllm.AutoModel can actually load a real model and
generate text. Follows testing-airllm.py pattern exactly, with
reduced max_new_tokens to keep the test fast.

Per docs/IMPLEMENTATION.md Step 1 — Library PoC.
Always test against real data.
"""

from __future__ import annotations

import pytest

from tests.pocs._cuda import has_cuda


def test_airllm_importable() -> None:
    """AirLLM package can be imported."""
    import airllm

    assert airllm is not None


def test_auto_model_accessible() -> None:
    """AutoModel class is accessible from airllm package."""
    from airllm import AutoModel

    assert AutoModel is not None
    assert hasattr(AutoModel, "from_pretrained")


def test_auto_model_signature() -> None:
    """AutoModel.from_pretrained accepts model_id and kwargs.

    Compression is passed via **kwargs.
    """
    import inspect

    from airllm import AutoModel

    sig = inspect.signature(AutoModel.from_pretrained)
    params = list(sig.parameters.keys())

    assert len(params) >= 1, "from_pretrained must accept a model identifier"
    assert "kwargs" in params, "from_pretrained must accept **kwargs for compression"


@pytest.mark.skipif(not has_cuda(), reason="CUDA not available — PoC requires GPU hardware")
def test_real_model_load_and_generate() -> None:
    """Load a real model via AirLLM and generate text.

    Follows testing-airllm.py pattern exactly, with reduced
    max_new_tokens to keep the test fast. Model is cached locally.
    """
    from airllm import AutoModel

    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    max_length = 128
    quant = "4bit"

    model = AutoModel.from_pretrained(model_name, compression=quant)

    input_text = [
        "What is the capital of United States?",
    ]

    input_tokens = model.tokenizer(
        input_text,
        return_tensors="pt",
        return_attention_mask=False,
        truncation=True,
        max_length=max_length,
        padding=False,
    )

    generation_output = model.generate(
        input_tokens["input_ids"].cuda(),
        max_new_tokens=4,
        use_cache=True,
        return_dict_in_generate=True,
    )

    output = model.tokenizer.decode(generation_output.sequences[0])

    assert isinstance(output, str), "Output must be a string"
    assert len(output) > 0, "Output must not be empty"
