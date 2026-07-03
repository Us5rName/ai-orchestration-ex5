"""HuggingFace Transformers inference provider.

Wraps ``transformers.AutoModelForCausalLM`` behind the
:class:`~airllm_benchmark.providers.base.InferenceProvider` protocol
so runners remain provider-agnostic.

Derived from Step 2 Feature PoCs (``pocs/transformers_feature_pocs.py``).
"""

from __future__ import annotations

import gc
from typing import TYPE_CHECKING

from transformers import AutoModelForCausalLM, AutoTokenizer

from .base import InferenceProvider

if TYPE_CHECKING:
    from transformers import PreTrainedModel


class TransformersProvider(InferenceProvider):
    """Inference provider backed by HuggingFace Transformers.

    Loads models via ``AutoModelForCausalLM`` and generates text
    through PyTorch tensors. Supports ``device`` configuration for
    CPU or CUDA targets.

    Args:
        device: Target device string (``"cpu"``, ``"cuda"``, ``"mps"``).
    """

    def __init__(self, device: str = "cpu") -> None:
        self._device = device
        self._model: PreTrainedModel | None = None
        self._tokenizer: AutoTokenizer | None = None
        self._model_id: str | None = None

    # ——— InferenceProvider: load_model ———

    def load_model(self, model_id: str, device: str | None = None) -> None:
        """Load model weights onto the target device.

        Caches tokenizer and model so repeated calls with the same
        ``model_id`` skip redundant downloads.

        Args:
            model_id: HuggingFace model identifier or local path.
            device: Target device (falls back to constructor ``device``).

        Raises:
            FileNotFoundError: If model cannot be found on HF Hub.
            RuntimeError: If model loading fails.
        """
        target = device or self._device

        # Reuse tokenizer if already loaded for this model.
        if self._tokenizer is not None and self._model_id == model_id:
            return

        self._model_id = model_id
        self._tokenizer = AutoTokenizer.from_pretrained(model_id)
        self._model = AutoModelForCausalLM.from_pretrained(model_id).to(target)

    # ——— InferenceProvider: generate ———

    def generate(self, prompt: str, max_tokens: int) -> str:
        """Generate text from a prompt.

        Args:
            prompt: Input text to complete.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated text string (excluding the original prompt).

        Raises:
            RuntimeError: If ``load_model`` has not been called.
            ValueError: If ``prompt`` is empty or ``max_tokens`` <= 0.
        """
        if self._model is None or self._tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() before generate().")
        if not prompt:
            raise ValueError("prompt must not be empty")
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        inputs = self._tokenizer(prompt, return_tensors="pt")
        outputs = self._model.generate(**inputs, max_new_tokens=max_tokens)
        # Decode full output, then strip the original prompt.
        full_text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        return full_text[len(prompt) :]

    # ——— InferenceProvider: unload ———

    def unload(self) -> None:
        """Free model weights and associated memory.

        Safe to call when no model is loaded.
        """
        if self._model is not None:
            del self._model
            self._model = None
        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None
        self._model_id = None
        gc.collect()

        # Clear CUDA cache if available; no-op on CPU.
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
