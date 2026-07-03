"""Tests for TransformersProvider.load_model()."""

from __future__ import annotations

import pytest

from airllm_benchmark.providers.transformers_provider import (
    TransformersProvider,
)
from tests.unit.conftest import mock_transformers


class TestLoadModel:
    """Tests for TransformersProvider.load_model()."""

    def test_load_stores_model_and_tokenizer(self, provider: TransformersProvider) -> None:
        with mock_transformers() as (_tok_cls, _model_cls, mock_tok, mock_model):
            provider.load_model("gpt2", "cpu")

            assert provider._tokenizer is mock_tok
            assert provider._model is mock_model

    def test_load_moves_model_to_device(self, provider: TransformersProvider) -> None:
        with mock_transformers() as (_tok_cls, _model_cls, _mock_tok, mock_model):
            provider.load_model("gpt2", "cuda")

            mock_model.to.assert_called_once_with("cuda")

    def test_load_reuses_tokenizer_if_already_loaded(self, provider: TransformersProvider) -> None:
        """Tokenizer is only loaded once per model_id."""
        with mock_transformers() as (mock_tok_cls, _model_cls, _mock_tok, _m):
            provider.load_model("gpt2", "cpu")
            provider.load_model("gpt2", "cpu")

            mock_tok_cls.from_pretrained.assert_called_once()

    def test_load_raises_on_failure(self, provider: TransformersProvider) -> None:
        with mock_transformers() as (mock_tok_cls, _model_cls, _mt, _mm):
            mock_tok_cls.from_pretrained.side_effect = FileNotFoundError("no model")
            with pytest.raises(FileNotFoundError):
                provider.load_model("nonexistent", "cpu")
