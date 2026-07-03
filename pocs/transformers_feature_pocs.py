"""Transformers Feature PoCs — Step 2 of IMPLEMENTATION.md.

One PoC per ``InferenceProvider`` interface method. Each isolates a
single concern and proves the feature can be implemented correctly
before building the full module.

Run:
    uv run python pocs/transformers_feature_pocs.py
"""

from __future__ import annotations

import gc
import weakref
from typing import Any

from transformers import AutoModelForCausalLM, AutoTokenizer

TINY_MODEL = "hf-internal-testing/tiny-random-gpt2"


# ——— Feature PoC: load_model ———


def poc_load_model(model_id: str, device: str = "cpu") -> dict[str, Any]:
    """Prove model can be loaded onto a target device.

    Returns tokenizer and model so caller can verify load succeeded.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id).to(device)

    return {"tokenizer": tokenizer, "model": model}


# ——— Feature PoC: generate ———


def poc_generate(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompt: str,
    max_tokens: int,
) -> str:
    """Prove generation respects ``max_tokens`` limit.

    Returns only the newly generated text (excluding the prompt).
    """
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=max_tokens)
    # Decode full output, then strip the original prompt to isolate
    # the generated portion.
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    generated = full_text[len(prompt) :]
    return generated


# ——— Feature PoC: unload ———


def poc_unload(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
) -> None:
    """Prove model and tokenizer can be freed from memory.

    Deletes references and runs garbage collection. On CUDA devices
    also clears the cached allocations so VRAM is reclaimed.
    """
    del model
    del tokenizer
    gc.collect()

    # Clear CUDA cache if available; no-op on CPU.
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


if __name__ == "__main__":
    # Demonstrate full lifecycle: load → generate → unload.
    artifacts = poc_load_model(TINY_MODEL, "cpu")
    result = poc_generate(
        artifacts["model"],
        artifacts["tokenizer"],
        "Once upon a time",
        max_tokens=16,
    )
    print(f"Generated: {result!r}")

    weak = weakref.ref(artifacts["model"])
    poc_unload(artifacts["model"], artifacts["tokenizer"])
    artifacts = None
    gc.collect()

    # If weak ref is dead, unload freed the model.
    print(f"Model freed: {weak() is None}")
