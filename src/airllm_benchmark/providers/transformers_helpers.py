"""Transformers provider configuration helpers.

Separates data-layer configuration (quantization) from the provider
service (TransformersProvider). Follows the same split pattern as
metrics_helpers.py / metrics.py and chart_helpers.py / visualizer.py.

Per modular-design: Single Responsibility — data configuration vs.
inference service.
"""

from __future__ import annotations

from transformers import BitsAndBytesConfig


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
