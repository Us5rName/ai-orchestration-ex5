"""Tests for TransformersProvider.generate()."""

from __future__ import annotations

import pytest

from airllm_benchmark.providers.transformers_provider import (
    TransformersProvider,
)
from tests.unit.conftest import mock_transformers


class TestGenerate:
    """Tests for TransformersProvider.generate()."""

    def test_generate_returns_text(self, provider: TransformersProvider) -> None:
        with mock_transformers(tokenizer_decode="Hello world this is text") as (_tc, _mc, _mt, _mm):
            provider.load_model("gpt2", "cpu")
            result = provider.generate("Hello", 16)

            assert result == " world this is text"

    def test_generate_raises_when_not_loaded(self, provider: TransformersProvider) -> None:
        with pytest.raises(RuntimeError, match="load_model"):
            provider.generate("test", 16)

    def test_generate_raises_on_empty_prompt(self, provider: TransformersProvider) -> None:
        with mock_transformers() as (_tc, _mc, _mt, _mm):
            provider.load_model("gpt2", "cpu")

        with pytest.raises(ValueError, match="prompt"):
            provider.generate("", 16)

    def test_generate_raises_on_negative_tokens(self, provider: TransformersProvider) -> None:
        with mock_transformers() as (_tc, _mc, _mt, _mm):
            provider.load_model("gpt2", "cpu")

        with pytest.raises(ValueError, match="max_tokens"):
            provider.generate("test", -1)
