"""Real device tests for TransformersProvider (CPU and GPU).

These tests load an actual tiny model and verify the provider works on
both CPU and CUDA. Skips GPU tests when CUDA is unavailable.
"""

from __future__ import annotations

import pytest
import torch

from airllm_benchmark.providers.transformers_provider import TransformersProvider

TINY_MODEL = "hf-internal-testing/tiny-random-gpt2"


class TestCpuPath:
    """Verify provider works on real CPU execution."""

    def test_load_and_generate_cpu(self) -> None:
        prov = TransformersProvider(device="cpu")
        prov.load_model(TINY_MODEL, device="cpu")

        result = prov.generate("Once upon a time", max_tokens=16)

        assert isinstance(result, str)
        assert len(result) > 0
        prov.unload()

    def test_unload_after_cpu_run(self) -> None:
        prov = TransformersProvider(device="cpu")
        prov.load_model(TINY_MODEL, device="cpu")
        prov.generate("Test", max_tokens=4)
        prov.unload()

        assert prov._model is None
        assert prov._tokenizer is None


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
class TestGpuPath:
    """Verify provider works on real CUDA execution."""

    def test_load_and_generate_cuda(self) -> None:
        prov = TransformersProvider(device="cuda")
        prov.load_model(TINY_MODEL, device="cuda")

        result = prov.generate("Once upon a time", max_tokens=16)

        assert isinstance(result, str)
        assert len(result) > 0
        prov.unload()

    def test_unload_after_cuda_run(self) -> None:
        prov = TransformersProvider(device="cuda")
        prov.load_model(TINY_MODEL, device="cuda")
        prov.generate("Test", max_tokens=4)
        prov.unload()

        assert prov._model is None
        assert prov._tokenizer is None
