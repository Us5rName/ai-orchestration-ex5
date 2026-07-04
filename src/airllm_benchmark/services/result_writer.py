"""Result persistence for inference benchmarking.

Serializes MetricsRecord instances to a JSON array file so results
survive across runs and can be consumed by the visualizer.  Per
PLAN.md C3 Component Diagram and Sequence Diagram (lines 199-200).

Separation of concerns:
    - ResultWriter (persistence service) lives here.
    - MetricsRecord (data contract) lives in metrics_helpers.py.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from .metrics_helpers import MetricsRecord

if TYPE_CHECKING:
    from collections.abc import Sequence


class ResultWriter:
    """Persists MetricsRecord instances to a JSON array file.

    Input:
        output_path (str): File path for metrics.json output.
    Output:
        None (side-effect: writes to file).
    Setup:
        output_path with parent directory existing.

    Per INTERFACES.md §7.
    """

    def __init__(self, output_path: str) -> None:
        """Initialize writer.

        Args:
            output_path: Path to JSON file (e.g. "results/metrics.json").
        """
        self._path = output_path

    def append(self, record: MetricsRecord) -> None:
        """Append a single metrics record to the JSON array file.

        Loads existing records if the file exists, appends the new
        record, and writes back.  Creates parent directories and the
        file itself if they do not exist yet.

        Args:
            record: MetricsRecord to persist.
        """
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        existing = _load_raw(self._path)
        existing.append(_to_dict(record))
        _dump(self._path, existing)

    def load(self) -> list[MetricsRecord]:
        """Load all persisted records from the JSON array file.

        Returns:
            List of MetricsRecord instances.  Empty list if file is
            missing or contains no records.
        """
        raw = _load_raw(self._path)
        return [_from_dict(item) for item in raw]

    def clear(self) -> None:
        """Replace the JSON file with an empty array.

        Use before a fresh benchmark run to discard stale data.
        No-ops silently if the file does not exist.
        """
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        _dump(self._path, [])


# ---------------------------------------------------------------------------
# Private helpers — kept thin so ResultWriter stays under 150 lines
# ---------------------------------------------------------------------------


def _to_dict(record: MetricsRecord) -> dict:
    """Convert a frozen MetricsRecord to a plain dict for JSON."""
    from dataclasses import asdict

    return asdict(record)


def _from_dict(item: dict) -> MetricsRecord:
    """Reconstruct a MetricsRecord from a JSON dict."""
    return MetricsRecord(**item)


def _load_raw(path: str) -> list[dict]:
    """Load raw dicts from *path*. Returns [] when file is absent."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _dump(path: str, data: Sequence[dict]) -> None:
    """Write *data* as an indented JSON array to *path*."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(list(data), f, indent=2)
