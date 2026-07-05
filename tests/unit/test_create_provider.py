"""Tests for the provider factory (create_provider)."""

import pytest

from airllm_benchmark.providers.llamacpp_provider import LlamaCppProvider
from airllm_benchmark.providers.transformers_provider import TransformersProvider
from airllm_benchmark.sdk.sdk_helpers import create_provider


def test_create_provider_transformers_cpu() -> None:
    """Test creating a Transformers provider with CPU device."""
    provider = create_provider(
        "transformers", {"transformers": {"device": "cpu"}}, quantization="none"
    )
    assert isinstance(provider, TransformersProvider)


def test_create_provider_transformers_gpu() -> None:
    """Test creating a Transformers provider with GPU device."""
    provider = create_provider(
        "transformers",
        {"transformers": {"device": "cuda"}},
        quantization="4bit",
    )
    assert isinstance(provider, TransformersProvider)


def test_create_provider_llamacpp_cpu() -> None:
    """Test creating an llama.cpp provider with CPU device."""
    provider = create_provider(
        "llamacpp", {"llamacpp": {"device": "cpu"}}, quantization="none"
    )
    assert isinstance(provider, LlamaCppProvider)


def test_create_provider_llamacpp_gpu() -> None:
    """Test creating an llama.cpp provider with GPU device."""
    provider = create_provider(
        "llamacpp",
        {"llamacpp": {"device": "cuda"}},
        quantization="none",
    )
    assert isinstance(provider, LlamaCppProvider)


def test_create_provider_unsupported() -> None:
    """Test creating an unsupported provider raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported provider: 'unknown'"):
        create_provider("unknown", {}, quantization="none")


def test_create_provider_error_message_includes_available() -> None:
    """Test that unsupported provider error lists available providers."""
    with pytest.raises(ValueError, match="transformers, llamacpp"):
        create_provider("unsupported_provider", {}, quantization="none")
