"""AirLLM model loading helpers.

Wraps airllm.AutoModel.from_pretrained with quantization support.
AirLLM uses paged inference — weights are loaded on-demand from disk,
allowing models larger than RAM to run with latency trade-offs.

Per docs/TODO.md task 5.4 and testing-airllm.py reference.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from airllm import AutoModel

# Supported quantization levels mapped to AirLLM compression strings.
_COMPRESSION_MAP: dict[str, str] = {
    "none": "",
    "4bit": "4bit",
    "8bit": "8bit",
}


def load_model(model_id: str, quantization: str = "none") -> AutoModel:
    """Load a model via AirLLM with optional quantization.

    AirLLM uses paged inference: model weights stay on disk and are
    loaded on-demand during inference. This allows running models
    larger than available RAM at the cost of higher latency.

    Args:
        model_id: HuggingFace model identifier or local path.
        quantization: Quantization level ("4bit", "8bit", "none").

    Returns:
        Loaded AirLLM AutoModel instance with built-in tokenizer.

    Raises:
        ValueError: If *quantization* is not a supported level.
        RuntimeError: If model loading fails (e.g. network error).
    """
    from airllm import AutoModel

    compression = _resolve_compression(quantization)

    # AirLLM loads weights on-demand; from_pretrained returns immediately
    # with a paged model reference rather than loading all weights at once.
    if compression:
        return AutoModel.from_pretrained(model_id, compression=compression)
    return AutoModel.from_pretrained(model_id)


def _resolve_compression(quantization: str) -> str:
    """Map quantization string to AirLLM compression value.

    Args:
        quantization: Quantization level ("4bit", "8bit", "none").

    Returns:
        Compression string for AirLLM (empty string means no compression).

    Raises:
        ValueError: If *quantization* is not a supported level.
    """
    if quantization not in _COMPRESSION_MAP:
        supported = ", ".join(sorted(_COMPRESSION_MAP))
        msg = f"Unsupported quantization: '{quantization}'. Must be one of: {supported}"
        raise ValueError(msg)
    return _COMPRESSION_MAP[quantization]
