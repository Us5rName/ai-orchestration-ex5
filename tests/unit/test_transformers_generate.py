"""Tests for TransformersProvider.generate()."""

from __future__ import annotations

import pytest

from airllm_benchmark.providers.transformers_provider import (
    TransformersProvider,
)
from tests.unit.conftest import mock_transformers


class TestGenerate:
    """Tests for TransformersProvider.generate()."""

    def test_generate_returns_tuple(self, provider: TransformersProvider) -> None:
        """generate() returns (text, token_count) tuple."""
        with mock_transformers(tokenizer_decode="Hello world this is text") as (_tc, _mc, _t, _mm):
            provider.load_model("gpt2", "cpu")
            text, token_count = provider.generate("Hello", 16)

            assert text == " world this is text"
            assert isinstance(token_count, int)
            assert token_count > 0

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
