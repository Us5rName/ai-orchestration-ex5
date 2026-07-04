"""Tests for LlamaCppProvider.generate()."""

from __future__ import annotations

import pytest

from airllm_benchmark.providers.llamacpp_provider import LlamaCppProvider
from tests.unit.conftest import mock_llamacpp


class TestGenerate:
    """Tests for LlamaCppProvider.generate()."""

    def test_generate_returns_tuple(self, llamacpp_provider: LlamaCppProvider) -> None:
        """generate() returns (text, token_count) tuple."""
        with mock_llamacpp(completion_text=" world", completion_tokens=2):
            llamacpp_provider.load_model("models/tiny.gguf", "cpu")
            text, token_count = llamacpp_provider.generate("hello", 16)

            assert text == " world"
            assert token_count == 2

    def test_generate_uses_usage_completion_tokens(
        self, llamacpp_provider: LlamaCppProvider
    ) -> None:
        with mock_llamacpp(completion_text="abc", completion_tokens=7, include_usage=True):
            llamacpp_provider.load_model("models/tiny.gguf", "cpu")
            _, token_count = llamacpp_provider.generate("hi", 16)

            assert token_count == 7

    def test_generate_falls_back_to_tokenize_when_no_usage(
        self, llamacpp_provider: LlamaCppProvider
    ) -> None:
        with mock_llamacpp(completion_text="abc", completion_tokens=4, include_usage=False) as (
            _cls,
            mock_llm,
        ):
            llamacpp_provider.load_model("models/tiny.gguf", "cpu")
            _, token_count = llamacpp_provider.generate("hi", 16)

            mock_llm.tokenize.assert_called_once_with(b"abc", add_bos=False)
            assert token_count == 4

    def test_generate_passes_max_tokens_through(
        self, llamacpp_provider: LlamaCppProvider
    ) -> None:
        with mock_llamacpp() as (_cls, mock_llm):
            llamacpp_provider.load_model("models/tiny.gguf", "cpu")
            llamacpp_provider.generate("hi", 42)

            mock_llm.create_completion.assert_called_once_with("hi", max_tokens=42)

    def test_generate_raises_when_not_loaded(self, llamacpp_provider: LlamaCppProvider) -> None:
        with pytest.raises(RuntimeError, match="load_model"):
            llamacpp_provider.generate("test", 16)

    def test_generate_raises_on_empty_prompt(self, llamacpp_provider: LlamaCppProvider) -> None:
        with mock_llamacpp():
            llamacpp_provider.load_model("models/tiny.gguf", "cpu")

        with pytest.raises(ValueError, match="prompt"):
            llamacpp_provider.generate("", 16)

    def test_generate_raises_on_negative_tokens(
        self, llamacpp_provider: LlamaCppProvider
    ) -> None:
        with mock_llamacpp():
            llamacpp_provider.load_model("models/tiny.gguf", "cpu")

        with pytest.raises(ValueError, match="max_tokens"):
            llamacpp_provider.generate("test", -1)
