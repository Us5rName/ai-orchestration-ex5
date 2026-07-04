"""Tests for LlamaCppProvider.load_model()."""

from __future__ import annotations

import pytest

from airllm_benchmark.providers.llamacpp_provider import LlamaCppProvider
from tests.unit.conftest import mock_llamacpp


class TestLoadModel:
    """Tests for LlamaCppProvider.load_model()."""

    def test_load_local_path_stores_model(self, llamacpp_provider: LlamaCppProvider) -> None:
        with mock_llamacpp() as (mock_llama_cls, mock_llm):
            llamacpp_provider.load_model("models/tiny.gguf", "cpu")

            assert llamacpp_provider._llm is mock_llm
            mock_llama_cls.assert_called_once_with(
                model_path="models/tiny.gguf", n_gpu_layers=0, verbose=False
            )

    def test_load_hf_hub_identifier_uses_from_pretrained(
        self, llamacpp_provider: LlamaCppProvider
    ) -> None:
        with mock_llamacpp() as (mock_llama_cls, mock_llm):
            llamacpp_provider.load_model("org/repo::model.Q4_0.gguf", "cpu")

            assert llamacpp_provider._llm is mock_llm
            mock_llama_cls.from_pretrained.assert_called_once_with(
                repo_id="org/repo", filename="model.Q4_0.gguf", n_gpu_layers=0, verbose=False
            )

    def test_load_maps_cuda_device_to_full_offload(
        self, llamacpp_provider: LlamaCppProvider
    ) -> None:
        with mock_llamacpp() as (mock_llama_cls, _mock_llm):
            llamacpp_provider.load_model("models/tiny.gguf", "cuda")

            mock_llama_cls.assert_called_once_with(
                model_path="models/tiny.gguf", n_gpu_layers=-1, verbose=False
            )

    def test_load_falls_back_to_constructor_device(self) -> None:
        prov = LlamaCppProvider(device="cuda")
        with mock_llamacpp() as (mock_llama_cls, _mock_llm):
            prov.load_model("models/tiny.gguf")

            mock_llama_cls.assert_called_once_with(
                model_path="models/tiny.gguf", n_gpu_layers=-1, verbose=False
            )

    def test_load_reuses_model_if_already_loaded(
        self, llamacpp_provider: LlamaCppProvider
    ) -> None:
        """Model is only (re)loaded once per model_id."""
        with mock_llamacpp() as (mock_llama_cls, _mock_llm):
            llamacpp_provider.load_model("models/tiny.gguf", "cpu")
            llamacpp_provider.load_model("models/tiny.gguf", "cpu")

            mock_llama_cls.assert_called_once()

    def test_load_raises_on_failure(self, llamacpp_provider: LlamaCppProvider) -> None:
        with mock_llamacpp() as (mock_llama_cls, _mock_llm):
            mock_llama_cls.side_effect = ValueError("model file not found")
            with pytest.raises(ValueError, match="not found"):
                llamacpp_provider.load_model("missing.gguf", "cpu")
