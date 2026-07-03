"""Inference provider protocol.

All providers in the providers/ layer implement this Protocol. A provider
handles model loading and text generation for a specific backend (Ollama,
Transformers, llama.cpp). Runners delegate to a configured provider so they
remain provider-agnostic.

See docs/INTERFACES.md §2 for the full contract.
"""

from typing import Protocol


class InferenceProvider(Protocol):
    """Interface for all inference providers.

    Each concrete provider wraps a different runtime (HTTP client, PyTorch
    model, native bindings) behind this uniform contract so runners and the
    SDK never depend on a specific backend.
    """

    def load_model(self, model_id: str, device: str) -> None:
        """Load model weights onto the target device.

        Args:
            model_id: HuggingFace model identifier or local path.
            device: Target device string (e.g. ``"cuda"``, ``"cpu"``, ``"mps"``).
        """
        ...

    def generate(self, prompt: str, max_tokens: int) -> str:
        """Generate text from a prompt.

        Args:
            prompt: Input text to complete.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated text string.
        """
        ...

    def unload(self) -> None:
        """Free model weights and associated memory.

        Called after inference completes so the next run can load a different
        model without accumulating memory pressure.
        """
        ...
