"""Shared fixtures for provider unit tests.

All external dependencies (transformers, torch) are mocked so tests
run without downloading models or requiring GPU hardware.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.providers.transformers_provider import (
    TransformersProvider,
)

_PROVIDER = "airllm_benchmark.providers.transformers_provider"


@pytest.fixture
def provider() -> TransformersProvider:
    """Return a fresh provider with default device."""
    return TransformersProvider(device="cpu")


@contextmanager
def mock_transformers(
    model_to_self: bool = True,
    tokenizer_decode: str = "",
) -> Iterator[tuple[MagicMock, MagicMock]]:
    """Patch AutoTokenizer and AutoModelForCausalLM for provider tests.

    Args:
        model_to_self: Make ``.to()`` return the model itself.
        tokenizer_decode: Value for ``tokenizer.decode()`` return.

    Yields:
        Tuple of (mock_tok_cls, mock_model_cls, mock_tokenizer, mock_model).
    """
    with (
        patch(f"{_PROVIDER}.AutoTokenizer") as mock_tok_cls,
        patch(f"{_PROVIDER}.AutoModelForCausalLM") as mock_model_cls,
    ):
        mock_tokenizer = MagicMock()
        if tokenizer_decode:
            mock_tokenizer.decode.return_value = tokenizer_decode
        mock_model = MagicMock()
        if model_to_self:
            mock_model.to.return_value = mock_model

        mock_tok_cls.from_pretrained.return_value = mock_tokenizer
        mock_model_cls.from_pretrained.return_value = mock_model

        yield mock_tok_cls, mock_model_cls, mock_tokenizer, mock_model
