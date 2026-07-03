"""Tests for Transformers Feature PoCs — Step 2.

Each ``InferenceProvider`` interface method has a dedicated PoC test.
Tests verify the PoC produces the expected output for its feature.

Run:
    uv run pytest tests/pocs/test_transformers_feature_pocs.py -v
"""

from __future__ import annotations

import gc
import weakref

from pocs.transformers_feature_pocs import (
    TINY_MODEL,
    poc_generate,
    poc_load_model,
    poc_unload,
)


class TestPoCLoadModel:
    """Feature PoC: load_model returns tokenizer + model."""

    def test_returns_tokenizer_and_model(self) -> None:
        artifacts = poc_load_model(TINY_MODEL, "cpu")

        assert "tokenizer" in artifacts
        assert "model" in artifacts

    def test_model_is_on_correct_device(self) -> None:
        artifacts = poc_load_model(TINY_MODEL, "cpu")

        # Model's parameters should be on the requested device.
        device = next(artifacts["model"].parameters()).device
        assert device.type == "cpu"


class TestPoCGenerate:
    """Feature PoC: generate respects max_tokens limit."""

    def test_generate_returns_non_empty(self) -> None:
        artifacts = poc_load_model(TINY_MODEL, "cpu")
        result = poc_generate(
            artifacts["model"],
            artifacts["tokenizer"],
            "Hello",
            max_tokens=16,
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_respects_max_tokens(self) -> None:
        """Assert generated text length is bounded by max_tokens."""
        artifacts = poc_load_model(TINY_MODEL, "cpu")
        max_tokens = 8
        result = poc_generate(
            artifacts["model"],
            artifacts["tokenizer"],
            "Test prompt",
            max_tokens=max_tokens,
        )
        # Tokenize the generated portion to count actual tokens.
        tokens = artifacts["tokenizer"](result, return_tensors="pt")
        assert tokens["input_ids"].shape[-1] <= max_tokens


class TestPoCUnload:
    """Feature PoC: unload frees model memory."""

    def test_unload_frees_model(self) -> None:
        """Assert unload releases all references so GC can collect."""
        artifacts = poc_load_model(TINY_MODEL, "cpu")
        # Create weak ref before passing to unload.
        weak = weakref.ref(artifacts["model"])

        poc_unload(artifacts["model"], artifacts["tokenizer"])
        # Clear the caller-side reference too — unload can only delete
        # the references it receives, not the ones the caller holds.
        del artifacts
        gc.collect()

        assert weak() is None
