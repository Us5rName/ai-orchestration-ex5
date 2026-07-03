"""Provider interface and protocol compliance tests.

Verifies that the InferenceProvider protocol is correctly defined and
that all concrete providers structurally satisfy the contract. All
external dependencies are mocked so tests run without downloading
models or requiring GPU hardware.

Corresponds to TODO item 3.6.
"""

from __future__ import annotations

from typing import Protocol

from airllm_benchmark.providers.base import InferenceProvider
from airllm_benchmark.providers.transformers_provider import (
    TransformersProvider,
)
from tests.unit.conftest import mock_transformers


class _MockProvider:
    """Minimal dummy provider for protocol verification."""

    def load_model(self, model_id: str, device: str) -> None:
        pass

    def generate(self, prompt: str, max_tokens: int) -> str:
        return "mock"

    def unload(self) -> None:
        pass


class TestInferenceProviderProtocol:
    """Tests for the InferenceProvider protocol definition."""

    def test_protocol_has_load_model(self) -> None:
        """Protocol declares load_model method."""
        assert hasattr(InferenceProvider, "load_model")

    def test_protocol_has_generate(self) -> None:
        """Protocol declares generate method."""
        assert hasattr(InferenceProvider, "generate")

    def test_protocol_has_unload(self) -> None:
        """Protocol declares unload method."""
        assert hasattr(InferenceProvider, "unload")

    def test_protocol_is_protocol_class(self) -> None:
        """InferenceProvider inherits from Protocol."""
        assert issubclass(InferenceProvider, Protocol)


class TestTransformersProtocolCompliance:
    """Verify TransformersProvider satisfies InferenceProvider contract."""

    def test_transformer_satisfies_protocol(self) -> None:
        """TransformersProvider structurally matches InferenceProvider."""
        provider: InferenceProvider = TransformersProvider(device="cpu")
        assert provider is not None

    def test_load_model_signature(self) -> None:
        """load_model accepts model_id and device parameters."""
        prov = TransformersProvider(device="cpu")
        with mock_transformers():
            prov.load_model("gpt2", "cpu")

    def test_load_model_with_optional_device(self) -> None:
        """load_model falls back to constructor device when device is None."""
        prov = TransformersProvider(device="cuda")
        with mock_transformers() as (_tc, _mc, _mt, mock_model):
            prov.load_model("gpt2")
            mock_model.to.assert_called_once_with("cuda")

    def test_generate_returns_str(self) -> None:
        """generate() returns a string."""
        prov = TransformersProvider(device="cpu")
        with mock_transformers(tokenizer_decode="hello world") as (_tc, _mc, _mt, _mm):
            prov.load_model("gpt2", "cpu")
            result = prov.generate("hello", 8)
            assert isinstance(result, str)

    def test_generate_strips_prompt(self) -> None:
        """generate() returns only the generated portion, not the prompt."""
        prov = TransformersProvider(device="cpu")
        with mock_transformers(tokenizer_decode="hello world") as (_tc, _mc, _mt, _mm):
            prov.load_model("gpt2", "cpu")
            result = prov.generate("hello", 8)
            assert result == " world"

    def test_unload_returns_none(self) -> None:
        """unload() returns None and does not raise."""
        prov = TransformersProvider(device="cpu")
        assert prov.unload() is None

    def test_protocol_methods_callable(self) -> None:
        """All protocol methods are callable on the provider."""
        prov = TransformersProvider(device="cpu")
        assert callable(prov.load_model)
        assert callable(prov.generate)
        assert callable(prov.unload)


class TestMockProviderCompliance:
    """Verify a minimal mock provider satisfies the protocol."""

    def test_mock_provider_satisfies_protocol(self) -> None:
        """A structurally correct class satisfies InferenceProvider."""
        provider: InferenceProvider = _MockProvider()
        assert provider is not None

    def test_mock_provider_load_model(self) -> None:
        """Mock provider load_model does not raise."""
        provider = _MockProvider()
        provider.load_model("test", "cpu")

    def test_mock_provider_generate(self) -> None:
        """Mock provider generate returns string."""
        provider = _MockProvider()
        result = provider.generate("test", 10)
        assert isinstance(result, str)

    def test_mock_provider_unload(self) -> None:
        """Mock provider unload does not raise."""
        provider = _MockProvider()
        provider.unload()


class TestProviderLifecycle:
    """Test the full provider lifecycle through the protocol interface."""

    def test_load_generate_unload_cycle(self) -> None:
        """Provider can load, generate, and unload in sequence."""
        prov: InferenceProvider = TransformersProvider(device="cpu")

        with mock_transformers(tokenizer_decode="input output") as (_tc, _mc, _mt, _mm):
            prov.load_model("gpt2", "cpu")
            result = prov.generate("input", 8)
            assert isinstance(result, str)

        prov.unload()

    def test_multiple_loads_same_model(self) -> None:
        """Repeated load_model calls with same model_id are idempotent."""
        prov = TransformersProvider(device="cpu")
        with mock_transformers() as (mock_tok_cls, _mc, _mt, _mm):
            prov.load_model("gpt2", "cpu")
            prov.load_model("gpt2", "cpu")
            mock_tok_cls.from_pretrained.assert_called_once()

    def test_reload_after_unload(self) -> None:
        """Provider can reload a model after unloading."""
        prov = TransformersProvider(device="cpu")
        with mock_transformers() as (mock_tok_cls, _mc, _mt, _mm):
            prov.load_model("gpt2", "cpu")
            prov.unload()
            prov.load_model("gpt2", "cpu")
            assert mock_tok_cls.from_pretrained.call_count == 2

    def test_unload_then_reload_different_model(self) -> None:
        """Provider can switch models after unload."""
        prov = TransformersProvider(device="cpu")
        with mock_transformers() as (mock_tok_cls, _mc, _mt, _mm):
            prov.load_model("gpt2", "cpu")
            prov.unload()
            prov.load_model("gpt2-medium", "cpu")
            assert mock_tok_cls.from_pretrained.call_count == 2
