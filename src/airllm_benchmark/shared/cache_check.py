"""HuggingFace local cache inspection — informational only.

Per docs/TODO.md task 7.4: validation reports whether configured models
are already present in ``~/.cache/huggingface`` so a benchmark run can
be planned without triggering a download. This never downloads or
modifies the cache — it only reads existing scan metadata.
"""

from __future__ import annotations


def model_cache_status(model_ids: list[str]) -> dict[str, bool]:
    """Return whether each of *model_ids* is present in the local HF cache.

    Args:
        model_ids: HuggingFace model identifiers to check
            (e.g. ``"Qwen/Qwen2.5-0.5B-Instruct"``).

    Returns:
        Dict mapping each model_id to ``True`` if at least one revision is
        cached locally, ``False`` otherwise (including if the cache scan
        itself fails, e.g. no cache directory exists yet).
    """
    try:
        from huggingface_hub import scan_cache_dir

        cached_ids = {repo.repo_id for repo in scan_cache_dir().repos}
    except Exception:  # noqa: BLE001 - any scan failure means "not cached"
        cached_ids = set()
    return {model_id: model_id in cached_ids for model_id in model_ids}
