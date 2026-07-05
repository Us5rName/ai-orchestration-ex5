"""Transformers provider configuration helpers.

Separates data-layer configuration (quantization) from the provider
service (TransformersProvider). Follows the same split pattern as
metrics_helpers.py / metrics.py and chart_helpers.py / visualizer.py.

Per modular-design: Single Responsibility — data configuration vs.
inference service.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    StoppingCriteria,
    StoppingCriteriaList,
)

from airllm_benchmark.shared.gatekeeper import call_with_rate_limit

if TYPE_CHECKING:
    import torch
    from transformers import PreTrainedModel, PreTrainedTokenizerBase


class FirstTokenCallback(StoppingCriteria):
    """Fires a callback the first time a generation step completes.

    ``StoppingCriteria.__call__`` runs once per generated token (including
    the first), which makes it a convenient, non-invasive hook for
    measuring real time-to-first-token without changing ``generate()``'s
    public signature. Always returns False — never actually stops
    generation.
    """

    def __init__(self, on_first_token: Callable[[], None]) -> None:
        """Store the callback to invoke on the first generation step."""
        self._on_first_token = on_first_token
        self._fired = False

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs: object) -> bool:
        """Invoke the callback once, then no-op; never requests a stop."""
        if not self._fired:
            self._fired = True
            self._on_first_token()
        return False


def build_generate_kwargs(
    max_tokens: int, on_first_token: Callable[[], None] | None
) -> dict[str, object]:
    """Build kwargs for ``model.generate()``, wiring the TTFT hook if set.

    Args:
        max_tokens: Maximum number of tokens to generate.
        on_first_token: Optional real-TTFT callback (see FirstTokenCallback).

    Returns:
        Kwargs dict for ``model.generate(**inputs, **kwargs)``.
    """
    kwargs: dict[str, object] = {"max_new_tokens": max_tokens}
    if on_first_token is not None:
        kwargs["stopping_criteria"] = StoppingCriteriaList([FirstTokenCallback(on_first_token)])
    return kwargs


def build_quant_config(quantization: str) -> BitsAndBytesConfig | None:
    """Build BitsAndBytesConfig for 4-bit or 8-bit quantization.

    Args:
        quantization: Quantization level ("4bit", "8bit", or "none").

    Returns:
        BitsAndBytesConfig instance or None if no quantization.
    """
    if quantization == "4bit":
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype="float16",
            bnb_4bit_use_double_quant=True,
        )
    if quantization == "8bit":
        return BitsAndBytesConfig(load_in_8bit=True)
    return None


def load_tokenizer_and_model(
    model_id: str, model_kwargs: dict
) -> tuple[PreTrainedTokenizerBase, PreTrainedModel]:
    """Load tokenizer + model from HF Hub through the API Gatekeeper.

    Args:
        model_id: HuggingFace model identifier or local path.
        model_kwargs: Extra kwargs for ``AutoModelForCausalLM.from_pretrained``.

    Returns:
        Tuple of (tokenizer, model), neither yet moved to a device.
    """
    tokenizer = call_with_rate_limit(
        "huggingface", lambda: AutoTokenizer.from_pretrained(model_id)
    )
    model = call_with_rate_limit(
        "huggingface", lambda: AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
    )
    return tokenizer, model


def clear_cuda_cache() -> None:
    """Clear CUDA cache if available; no-op on CPU or if torch is missing."""
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass
