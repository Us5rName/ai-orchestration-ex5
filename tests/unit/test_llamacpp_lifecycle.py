"""LlamaCppProvider lifecycle and protocol compliance tests.

Verifies that LlamaCppProvider satisfies the InferenceProvider contract
and exercises the full load-generate-unload lifecycle. All external
dependencies (``llama_cpp.Llama``) are mocked so tests run without
downloading GGUF models or requiring native llama.cpp bindings.

Corresponds to TODO item 3.5 / 3.6.
"""

from __future__ import annotations

from airllm_benchmark.providers.base import InferenceProvider
from airllm_benchmark.providers.llamacpp_provider import LlamaCppProvider
from tests.unit.conftest import mock_llamacpp


class TestLlamaCppProtocolCompliance:
    """Verify LlamaCppProvider satisfies InferenceProvider contract."""

    def test_llamacpp_satisfies_protocol(self) -> None:
        """LlamaCppProvider structurally matches InferenceProvider."""
        provider: InferenceProvider = LlamaCppProvider(device="cpu")
        assert provider is not None

    def test_load_model_signature(self) -> None:
        """load_model accepts model_id and device parameters."""
        prov = LlamaCppProvider(device="cpu")
        with mock_llamacpp():
            prov.load_model("models/tiny.gguf", "cpu")

    def test_generate_returns_tuple(self) -> None:
        """generate() returns (text, token_count) tuple."""
        prov = LlamaCppProvider(device="cpu")
        with mock_llamacpp(completion_text="hello world"):
            prov.load_model("models/tiny.gguf", "cpu")
            text, token_count = prov.generate("hello", 8)
            assert isinstance(text, str)
            assert isinstance(token_count, int)

    def test_unload_returns_none(self) -> None:
        """unload() returns None and does not raise."""
        prov = LlamaCppProvider(device="cpu")
        assert prov.unload() is None

    def test_protocol_methods_callable(self) -> None:
        """All protocol methods are callable on the provider."""
        prov = LlamaCppProvider(device="cpu")
        assert callable(prov.load_model)
        assert callable(prov.generate)
        assert callable(prov.unload)


class TestLlamaCppProviderLifecycle:
    """Test the full LlamaCppProvider lifecycle through the protocol."""

    def test_load_generate_unload_cycle(self) -> None:
        """Provider can load, generate, and unload in sequence."""
        prov: InferenceProvider = LlamaCppProvider(device="cpu")

        with mock_llamacpp(completion_text="input output"):
            prov.load_model("models/tiny.gguf", "cpu")
            text, _ = prov.generate("input", 8)
            assert isinstance(text, str)

        prov.unload()

    def test_multiple_loads_same_model(self) -> None:
        """Repeated load_model calls with same model_id are idempotent."""
        prov = LlamaCppProvider(device="cpu")
        with mock_llamacpp() as (mock_llama_cls, _mm):
            prov.load_model("models/tiny.gguf", "cpu")
            prov.load_model("models/tiny.gguf", "cpu")
            mock_llama_cls.assert_called_once()

    def test_reload_after_unload(self) -> None:
        """Provider can reload a model after unloading."""
        prov = LlamaCppProvider(device="cpu")
        with mock_llamacpp() as (mock_llama_cls, _mm):
            prov.load_model("models/tiny.gguf", "cpu")
            prov.unload()
            prov.load_model("models/tiny.gguf", "cpu")
            assert mock_llama_cls.call_count == 2
