"""Tests for shared/cache_check.py — HuggingFace cache inspection.

Mocks huggingface_hub.scan_cache_dir so tests never touch the real
local cache or network. Per docs/TODO.md task 7.4.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.shared.cache_check import model_cache_status


def _fake_scan(repo_ids: list[str]) -> MagicMock:
    """Build a scan_cache_dir()-shaped mock with the given cached repo ids."""
    info = MagicMock()
    info.repos = [MagicMock(repo_id=repo_id) for repo_id in repo_ids]
    return info


class TestModelCacheStatus:
    """Tests for model_cache_status()."""

    def test_reports_cached_model(self) -> None:
        """A model present in the scan result is reported as cached."""
        with patch("huggingface_hub.scan_cache_dir", return_value=_fake_scan(["org/model-a"])):
            status = model_cache_status(["org/model-a"])
        assert status == {"org/model-a": True}

    def test_reports_missing_model(self) -> None:
        """A model absent from the scan result is reported as not cached."""
        with patch("huggingface_hub.scan_cache_dir", return_value=_fake_scan(["org/other"])):
            status = model_cache_status(["org/model-a"])
        assert status == {"org/model-a": False}

    def test_handles_multiple_models(self) -> None:
        """Each requested model_id gets its own independent status."""
        with patch("huggingface_hub.scan_cache_dir", return_value=_fake_scan(["org/model-a"])):
            status = model_cache_status(["org/model-a", "org/model-b"])
        assert status == {"org/model-a": True, "org/model-b": False}

    def test_scan_failure_reports_all_not_cached(self) -> None:
        """A scan_cache_dir() failure is treated as 'nothing is cached'."""
        with patch("huggingface_hub.scan_cache_dir", side_effect=OSError("no cache")):
            status = model_cache_status(["org/model-a", "org/model-b"])
        assert status == {"org/model-a": False, "org/model-b": False}

    def test_empty_model_list_returns_empty_dict(self) -> None:
        """No models requested means no entries in the result."""
        with patch("huggingface_hub.scan_cache_dir", return_value=_fake_scan([])):
            assert model_cache_status([]) == {}
