"""Table formatting helpers for Visualizer.

Generates formatted comparison tables from MetricsRecord data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .metrics import MetricsRecord

# Columns displayed in the comparison table.
_TABLE_COLUMNS: list[tuple[str, str]] = [
    ("Mode", "mode"),
    ("Provider", "provider"),
    ("Runtime (s)", "total_runtime_s"),
    ("Peak RAM (MB)", "peak_ram_mb"),
    ("Status", "status"),
]


def _format_value(record: MetricsRecord, field: str) -> str:
    """Format a single field value for table display.

    Floats are rounded to 2 decimal places for readability.

    Args:
        record: The metrics record.
        field: The field name to extract.

    Returns:
        Formatted string value.
    """
    value = getattr(record, field)
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def format_comparison_table(records: list[MetricsRecord]) -> str:
    """Generate a formatted comparison table from metrics records.

    Produces a pipe-delimited table suitable for printing or saving
    to a markdown/text report.

    Args:
        records: List of metrics records to tabulate.

    Returns:
        Formatted table string.
    """
    if not records:
        return "No records to display."

    headers = [col[0] for col in _TABLE_COLUMNS]
    fields = [col[1] for col in _TABLE_COLUMNS]

    # Calculate column widths based on content.
    col_widths = [len(h) for h in headers]
    rows: list[list[str]] = []
    for record in records:
        row = [_format_value(record, field) for field in fields]
        rows.append(row)
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # Build separator line.
    separator = "+".join("-" * (w + 2) for w in col_widths) + "+"

    # Format header row.
    header_row = "|" + "|".join(h.center(w) for h, w in zip(headers, col_widths, strict=True)) + "|"

    # Format data rows.
    data_rows: list[str] = []
    for row in rows:
        data_row = (
            "|" + "|".join(cell.center(w) for cell, w in zip(row, col_widths, strict=True)) + "|"
        )
        data_rows.append(data_row)

    return "\n".join([separator, header_row, separator] + data_rows + [separator])
