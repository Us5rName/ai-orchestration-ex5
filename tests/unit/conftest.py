"""Shared fixtures for unit tests.

All external dependencies (transformers, torch) are mocked so tests
run without downloading models or requiring GPU hardware.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.providers.llamacpp_provider import LlamaCppProvider
from airllm_benchmark.providers.transformers_provider import (
    TransformersProvider,
)

# Import sample_records/mock_record fixtures so pytest discovers them
from tests.unit.fixtures_cli import mock_record  # noqa: F401
from tests.unit.fixtures_metrics import sample_records  # noqa: F401

_PROVIDER = "airllm_benchmark.providers.transformers_helpers"
_LLAMACPP_HELPERS = "airllm_benchmark.providers.llamacpp_helpers"


@pytest.fixture
def provider() -> TransformersProvider:
    """Return a fresh provider with default device."""
    return TransformersProvider(device="cpu")


@pytest.fixture
def llamacpp_provider() -> LlamaCppProvider:
    """Return a fresh LlamaCppProvider with default device."""
    return LlamaCppProvider(device="cpu")


@contextmanager
def mock_llamacpp(
    completion_text: str = "",
    completion_tokens: int = 3,
    include_usage: bool = True,
) -> Iterator[tuple[MagicMock, MagicMock]]:
    """Patch ``llama_cpp.Llama`` for LlamaCppProvider tests.

    Configures both the constructor (local-path load) and
    ``from_pretrained()`` (HF-Hub load) to return the same mock instance.

    Args:
        completion_text: Value for ``create_completion()``'s generated text.
        completion_tokens: Token count reported in ``usage.completion_tokens``,
            and used to size the ``tokenize()`` fallback return value.
        include_usage: Whether the mocked response includes a ``usage`` dict.
            Set ``False`` to exercise the ``tokenize()``-based fallback path.

    Yields:
        Tuple of (mock_llama_cls, mock_llm) — the patched ``Llama`` class
        and the instance returned by both its constructor and
        ``from_pretrained()``.
    """
    with patch(f"{_LLAMACPP_HELPERS}.Llama") as mock_llama_cls:
        mock_llm = MagicMock()
        response: dict = {"choices": [{"text": completion_text}]}
        if include_usage:
            response["usage"] = {"completion_tokens": completion_tokens}
        mock_llm.create_completion.return_value = response
        mock_llm.tokenize.return_value = list(range(max(1, completion_tokens)))
        mock_llama_cls.return_value = mock_llm
        mock_llama_cls.from_pretrained.return_value = mock_llm

        yield mock_llama_cls, mock_llm


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


@pytest.fixture
def mock_config() -> MagicMock:
    """Return a mocked ExperimentConfig."""
    config = MagicMock()
    config.models = {"small": {"id": "test/small", "tier": "small"}}
    config.prompts = {"P1": "Hello"}
    config.max_new_tokens = 32
    config.quantization = "none"
    config.gpu_provider = "transformers"
    config.cpu_baseline_provider = "transformers"
    config.provider_config = {"transformers": {"device": "cpu"}}
    config.get_model_id.return_value = "test/small"
    config.get_prompt.return_value = "Hello"
    return config


@pytest.fixture
def mock_hw() -> MagicMock:
    """Return a mocked HardwareConfig."""
    hw = MagicMock()
    hw.is_complete.return_value = True
    return hw
