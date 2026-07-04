"""Tests for LlamaCppProvider.unload() and protocol compliance."""

from __future__ import annotations

from airllm_benchmark.providers.llamacpp_provider import LlamaCppProvider
from tests.unit.conftest import mock_llamacpp


class TestUnload:
    """Tests for LlamaCppProvider.unload()."""

    def test_unload_clears_references(self, llamacpp_provider: LlamaCppProvider) -> None:
        with mock_llamacpp():
            llamacpp_provider.load_model("models/tiny.gguf", "cpu")

        llamacpp_provider.unload()

        assert llamacpp_provider._llm is None
        assert llamacpp_provider._model_id is None

    def test_unload_is_safe_when_not_loaded(self, llamacpp_provider: LlamaCppProvider) -> None:
        """Calling unload on an unloaded provider does not raise."""
        llamacpp_provider.unload()

    def test_unload_allows_reload_with_new_model(
        self, llamacpp_provider: LlamaCppProvider
    ) -> None:
        with mock_llamacpp() as (mock_llama_cls, _mock_llm):
            llamacpp_provider.load_model("models/tiny.gguf", "cpu")
            llamacpp_provider.unload()
            llamacpp_provider.load_model("models/other.gguf", "cpu")

            assert mock_llama_cls.call_count == 2


class TestProtocolCompliance:
    """Verify LlamaCppProvider satisfies InferenceProvider."""

    def test_has_required_methods(self) -> None:
        provider = LlamaCppProvider(device="cpu")
        assert callable(provider.load_model)
        assert callable(provider.generate)
        assert callable(provider.unload)
