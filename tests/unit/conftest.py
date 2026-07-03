"""Shared fixtures for unit tests.

All external dependencies (transformers, torch) are mocked so tests
run without downloading models or requiring GPU hardware.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.providers.transformers_provider import (
    TransformersProvider,
)

if TYPE_CHECKING:
    from airllm_benchmark.services.metrics import MetricsRecord

_PROVIDER = "airllm_benchmark.providers.transformers_provider"


@pytest.fixture
def provider() -> TransformersProvider:
    """Return a fresh provider with default device."""
    return TransformersProvider(device="cpu")


@pytest.fixture
def sample_records() -> list[MetricsRecord]:
    """Deterministic MetricsRecord instances for visualizer tests.

    Three records covering all inference modes: GPU, CPU, AirLLM.
    Imported lazily to avoid circular dependency at module level.
    """
    from airllm_benchmark.services.metrics import MetricsRecord

    return [
        MetricsRecord(
            run_id="run_001",
            model="test/small",
            mode="gpu_provider",
            provider="ollama",
            prompt="Hello",
            prompt_id="P1",
            quantization="none",
            max_new_tokens=32,
            load_time_s=0.5,
            ttft_s=0.5,
            total_runtime_s=1.2,
            tokens_generated=20,
            peak_ram_mb=450.0,
            peak_vram_mb=200.0,
            status="success",
            error="",
            timestamp="2024-01-01T00:00:00+00:00",
        ),
        MetricsRecord(
            run_id="run_002",
            model="test/large",
            mode="cpu_baseline",
            provider="transformers",
            prompt="Hello",
            prompt_id="P1",
            quantization="none",
            max_new_tokens=32,
            load_time_s=10.0,
            ttft_s=10.0,
            total_runtime_s=45.0,
            tokens_generated=20,
            peak_ram_mb=1800.0,
            peak_vram_mb=0.0,
            status="success",
            error="",
            timestamp="2024-01-01T00:01:00+00:00",
        ),
        MetricsRecord(
            run_id="run_003",
            model="test/large",
            mode="airllm",
            provider="airllm",
            prompt="Hello",
            prompt_id="P1",
            quantization="4bit",
            max_new_tokens=32,
            load_time_s=3.0,
            ttft_s=3.0,
            total_runtime_s=12.5,
            tokens_generated=20,
            peak_ram_mb=900.0,
            peak_vram_mb=0.0,
            status="success",
            error="",
            timestamp="2024-01-01T00:02:00+00:00",
        ),
    ]


@contextmanager
def mock_transformers(
    model_to_self: bool = True,
    tokenizer_decode: str = "",
) -> Iterator[tuple[MagicMock, MagicMock]]:
    """Patch AutoTokenizer and AutoModelForCausalLM for provider tests.

    Args:
        model_to_self: Make ``.to()`` return the model itself.
        tokenizer_decode: Value for ``tokenizer.decode()`` return.

    Yields:
        Tuple of (mock_tok_cls, mock_model_cls, mock_tokenizer, mock_model).
    """
    with (
        patch(f"{_PROVIDER}.AutoTokenizer") as mock_tok_cls,
        patch(f"{_PROVIDER}.AutoModelForCausalLM") as mock_model_cls,
    ):
        mock_tokenizer = MagicMock()
        if tokenizer_decode:
            mock_tokenizer.decode.return_value = tokenizer_decode
        mock_model = MagicMock()
        if model_to_self:
            mock_model.to.return_value = mock_model

        mock_tok_cls.from_pretrained.return_value = mock_tokenizer
        mock_model_cls.from_pretrained.return_value = mock_model

        yield mock_tok_cls, mock_model_cls, mock_tokenizer, mock_model
