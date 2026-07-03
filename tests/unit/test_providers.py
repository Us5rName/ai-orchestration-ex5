"""Provider interface and protocol compliance tests.

Verifies that the InferenceProvider protocol is correctly defined and
that structurally correct classes satisfy the contract. All external
dependencies are mocked so tests run without downloading models or
requiring GPU hardware.

Corresponds to TODO item 3.6.
"""

from __future__ import annotations

from typing import Protocol

from airllm_benchmark.providers.base import InferenceProvider


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
