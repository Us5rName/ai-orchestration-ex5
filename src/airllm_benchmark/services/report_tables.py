"""Full comparison table + CSV export for the reporting layer (§5.1).

New, additive module — does not modify table_helpers.py.
"""

from __future__ import annotations

import csv
import dataclasses
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from .metrics import MetricsRecord

# Full §5.1 column set: header label -> MetricsRecord field name.
_FULL_COLUMNS: list[tuple[str, str]] = [
    ("Model", "model"),
    ("Tier", "__tier__"),
    ("Mode", "mode"),
    ("Load (s)", "load_time_s"),
    ("TTFT (s)", "ttft_s"),
    ("Runtime (s)", "total_runtime_s"),
    ("Throughput (tok/s)", "generation_throughput"),
    ("Peak RAM (MB)", "peak_ram_mb"),
    ("Peak VRAM (MB)", "peak_vram_mb"),
    ("Status", "status"),
]


def _format_value(record: MetricsRecord, tier: str, field: str) -> str:
    """Format a single field value for table display.

    Floats are rounded to 2 decimal places for readability. The
    synthetic "__tier__" field pulls from the resolved tier instead
    of the record itself.
    """
    if field == "__tier__":
        return tier
    value = getattr(record, field)
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def format_full_comparison_table(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
) -> str:
    """Generate the full §5.1 comparison table (all required columns).

    Args:
        records: Metrics records to tabulate.
        tier_lookup: Callable mapping a model id to its tier name.

    Returns:
        Pipe-delimited ASCII table string.
    """
    if not records:
        return "No records to display."

    headers = [col[0] for col in _FULL_COLUMNS]
    fields = [col[1] for col in _FULL_COLUMNS]

    col_widths = [len(h) for h in headers]
    rows: list[list[str]] = []
    for record in records:
        tier = tier_lookup(record.model)
        row = [_format_value(record, tier, field) for field in fields]
        rows.append(row)
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    separator = "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_row = "|" + "|".join(h.center(w) for h, w in zip(headers, col_widths, strict=True)) + "|"
    data_rows = [
        "|" + "|".join(cell.center(w) for cell, w in zip(row, col_widths, strict=True)) + "|"
        for row in rows
    ]

    return "\n".join([separator, header_row, separator] + data_rows + [separator])


def export_metrics_csv(
    records: list[MetricsRecord],
    tier_lookup: Callable[[str], str],
    output_path: str = "assets/metrics.csv",
) -> str:
    """Export all 18 MetricsRecord fields + derived tier to CSV.

    Args:
        records: Metrics records to export.
        tier_lookup: Callable mapping a model id to its tier name.
        output_path: Destination CSV file path.

    Returns:
        Absolute path to the written CSV file.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [f.name for f in dataclasses.fields(records[0])] + ["tier"] if records else []
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames or ["tier"])
        writer.writeheader()
        for record in records:
            row = dataclasses.asdict(record)
            row["tier"] = tier_lookup(record.model)
            writer.writerow(row)

    return os.path.abspath(output_path)
