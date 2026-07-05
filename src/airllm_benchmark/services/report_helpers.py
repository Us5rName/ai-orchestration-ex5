"""Shared lookups and shaping helpers for the reporting layer.

Pure, read-only consumers of MetricsRecord + ExperimentConfig. No
existing visualizer/table/chart code is touched or imported here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from airllm_benchmark.shared.config_models import ExperimentConfig

    from .metrics import MetricsRecord

# Fixed per-mode color mapping per BENCHMARK.md §5.2 recommendation
# (GPU = blue, CPU = orange, AirLLM = green).
MODE_COLORS: dict[str, str] = {
    "gpu_provider": "#2196F3",
    "cpu_baseline": "#FF9800",
    "airllm": "#4CAF50",
}

# Tier sort order per BENCHMARK.md §5.2 recommendation (small -> large).
TIER_ORDER: list[str] = ["small", "medium", "large", "unknown"]


def resolve_tier(model_id: str, experiment: ExperimentConfig) -> str:
    """Map a HuggingFace model id to its configured tier name.

    Args:
        model_id: HuggingFace model identifier (MetricsRecord.model).
        experiment: Loaded experiment config with tier->model mapping.

    Returns:
        Tier name ("small"/"medium"/"large"), or "unknown" on miss.
    """
    for tier_name, tier_info in experiment.models.items():
        if tier_info.get("id") == model_id:
            return tier_info.get("tier", tier_name)
    return "unknown"


def tier_sort_key(tier: str) -> int:
    """Sort key placing tiers in small -> medium -> large -> unknown order."""
    return TIER_ORDER.index(tier) if tier in TIER_ORDER else len(TIER_ORDER)


def group_by_tier_and_mode(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
) -> dict[tuple[str, str], list[MetricsRecord]]:
    """Group records by (tier, mode) key.

    Args:
        records: Metrics records to group.
        tier_lookup: Callable mapping a model id to its tier name.

    Returns:
        Dict keyed by (tier, mode) with the matching records as values.
    """
    groups: dict[tuple[str, str], list[MetricsRecord]] = {}
    for record in records:
        key = (tier_lookup(record.model), record.mode)
        groups.setdefault(key, []).append(record)
    return groups


def sorted_group_keys(groups: dict[tuple[str, str], list[MetricsRecord]]) -> list[tuple[str, str]]:
    """Return (tier, mode) keys sorted by tier order then mode name."""
    return sorted(groups.keys(), key=lambda k: (tier_sort_key(k[0]), k[1]))
