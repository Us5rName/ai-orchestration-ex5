"""Tests for TransformersProvider.unload() and protocol compliance."""

from __future__ import annotations

from airllm_benchmark.providers.transformers_provider import (
    TransformersProvider,
)
from tests.unit.conftest import mock_transformers


class TestUnload:
    """Tests for TransformersProvider.unload()."""

    def test_unload_clears_references(self, provider: TransformersProvider) -> None:
        with mock_transformers() as (_tc, _mc, _mt, _mm):
            provider.load_model("gpt2", "cpu")

        provider.unload()

        assert provider._model is None
        assert provider._tokenizer is None

    def test_unload_is_safe_when_not_loaded(self, provider: TransformersProvider) -> None:
        """Calling unload on an unloaded provider does not raise."""
        provider.unload()


class TestProtocolCompliance:
    """Verify TransformersProvider satisfies InferenceProvider."""

    def test_has_required_methods(self) -> None:
        provider = TransformersProvider(device="cpu")
        assert callable(provider.load_model)
        assert callable(provider.generate)
        assert callable(provider.unload)
