"""llama.cpp inference provider.

Wraps ``llama_cpp.Llama`` behind the InferenceProvider protocol so runners
remain provider-agnostic. Supports both local ``.gguf`` files and models
fetched from the HuggingFace Hub via ``Llama.from_pretrained()``.
"""

from __future__ import annotations

import gc
from typing import TYPE_CHECKING

from . import llamacpp_helpers as _helpers
from .base import InferenceProvider

if TYPE_CHECKING:
    from llama_cpp import Llama


class LlamaCppProvider(InferenceProvider):
    """Inference provider backed by llama.cpp Python bindings.

    Loads GGUF models via ``llama_cpp.Llama`` and generates text through
    its completion API. Supports ``device`` configuration by mapping to
    llama.cpp's ``n_gpu_layers`` parameter (``0`` = CPU-only, ``-1`` = all
    layers offloaded to GPU).

    Args:
        device: Target device string (``"cpu"``, ``"cuda"``, ``"mps"``).
    """

    def __init__(self, device: str = "cpu") -> None:
        """Store the target device; model loads lazily via ``load_model``."""
        self._device = device
        self._llm: Llama | None = None
        self._model_id: str | None = None

    # ——— InferenceProvider: load_model ———

    def load_model(self, model_id: str, device: str | None = None) -> None:
        """Load GGUF model weights onto the target device.

        Caches the loaded model so repeated calls with the same
        ``model_id`` skip redundant loads/downloads.

        Args:
            model_id: Local ``.gguf`` file path, or a HuggingFace-Hub
                identifier of the form ``"repo_id::filename"`` resolvable
                by ``llama_cpp.Llama.from_pretrained()``.
            device: Target device (falls back to constructor ``device``).

        Raises:
            ValueError: If the local model file cannot be found.
            RuntimeError: If model loading fails.
        """
        target = device or self._device

        # Reuse the loaded model if already loaded for this model_id.
        if self._llm is not None and self._model_id == model_id:
            return

        # Sync instance device so a later reload uses the same target.
        self._device = target
        self._model_id = model_id

        n_gpu_layers = _helpers.resolve_n_gpu_layers(target)
        self._llm = _helpers.load_llama_model(model_id, n_gpu_layers)

    # ——— InferenceProvider: generate ———

    def generate(self, prompt: str, max_tokens: int) -> tuple[str, int]:
        """Generate text from a prompt.

        Args:
            prompt: Input text to complete.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            Tuple of (generated_text, actual_token_count). Token count is
            the number of tokens in the generated output (excluding prompt).

        Raises:
            RuntimeError: If ``load_model`` has not been called.
            ValueError: If ``prompt`` is empty or ``max_tokens`` <= 0.
        """
        if self._llm is None:
            raise RuntimeError("Model not loaded. Call load_model() before generate().")
        if not prompt:
            raise ValueError("prompt must not be empty")
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        response = self._llm.create_completion(prompt, max_tokens=max_tokens)
        generated_text = response["choices"][0]["text"]
        token_count = _helpers.count_completion_tokens(
            self._llm, generated_text, response.get("usage")
        )
        return generated_text, token_count

    # ——— InferenceProvider: unload ———

    def unload(self) -> None:
        """Free model weights and associated memory.

        Safe to call when no model is loaded.
        """
        if self._llm is not None:
            del self._llm
            self._llm = None
        self._model_id = None
        gc.collect()
