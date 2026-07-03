"""Tests for Transformers Library PoC — Step 1.

Verifies the `transformers` library is importable and can load a tiny
model + generate text. This test downloads the tiny model on first run
and caches it for subsequent executions.

Run:
    uv run pytest tests/pocs/test_transformers_library_poc.py -v
"""

from __future__ import annotations

from pocs.transformers_library_poc import load_and_generate


class TestTransformersLibraryPoC:
    """Tests for transformers library PoC."""

    def test_generate_returns_non_empty_string(self) -> None:
        """Assert PoC produces valid non-empty output."""
        result = load_and_generate()

        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_contains_prompt(self) -> None:
        """Assert generated text includes the original prompt."""
        prompt = "Hello, world!"
        result = load_and_generate(prompt)

        assert prompt in result

    def test_generate_with_custom_prompt(self) -> None:
        """Assert PoC works with arbitrary prompt text."""
        result = load_and_generate("The quick brown fox")

        assert isinstance(result, str)
        assert "The quick brown fox" in result
