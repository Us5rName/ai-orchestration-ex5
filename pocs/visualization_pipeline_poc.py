"""Minimal Metrics + Visualization Pipeline PoC.

Proves the full pipeline works: fake metrics records -> bar chart -> PNG output.
Uses real matplotlib against fake MetricsRecord data. No external dependencies
beyond what's already in the project (matplotlib, dataclasses).

Per IMPLEMENTATION.md Step 1: verify library (matplotlib) produces valid PNG
from synthetic benchmark data before building services/visualizer.py.

Run:
    uv run python pocs/visualization_pipeline_poc.py
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


@dataclass
class FakeMetricsRecord:
    """Minimal metrics record for PoC testing.

    Subset of the real MetricsRecord (INTERFACES.md §4) containing only
    the fields needed for visualization.
    """

    mode: str
    total_runtime_s: float
    peak_ram_mb: float


def generate_fake_records() -> list[FakeMetricsRecord]:
    """Generate fake benchmark results for three inference modes.

    Returns realistic-looking metrics for GPU, CPU, and AirLLM scenarios.
    """
    return [
        FakeMetricsRecord(mode="gpu_provider", total_runtime_s=1.2, peak_ram_mb=450.0),
        FakeMetricsRecord(mode="cpu_baseline", total_runtime_s=45.0, peak_ram_mb=1800.0),
        FakeMetricsRecord(mode="airllm", total_runtime_s=12.5, peak_ram_mb=900.0),
    ]


def generate_latency_bar_chart(
    records: list[FakeMetricsRecord],
    output_path: str,
) -> str:
    """Generate a bar chart comparing total_runtime_s across modes.

    Args:
        records: List of fake metrics records.
        output_path: File path for the output PNG.

    Returns:
        Absolute path to the generated PNG file.
    """
    modes = [r.mode for r in records]
    runtimes = [r.total_runtime_s for r in records]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(modes, runtimes, color=["#2196F3", "#F44336", "#4CAF50"])
    ax.set_ylabel("Total Runtime (seconds)")
    ax.set_title("Inference Latency Comparison")
    ax.set_ylim(0, max(runtimes) * 1.15)

    fig.tight_layout()
    fig.savefig(output_path, dpi=100)
    plt.close(fig)

    return os.path.abspath(output_path)


def generate_memory_bar_chart(
    records: list[FakeMetricsRecord],
    output_path: str,
) -> str:
    """Generate a bar chart comparing peak_ram_mb across modes.

    Args:
        records: List of fake metrics records.
        output_path: File path for the output PNG.

    Returns:
        Absolute path to the generated PNG file.
    """
    modes = [r.mode for r in records]
    ram_values = [r.peak_ram_mb for r in records]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(modes, ram_values, color=["#2196F3", "#F44336", "#4CAF50"])
    ax.set_ylabel("Peak RAM (MB)")
    ax.set_title("Memory Usage Comparison")
    ax.set_ylim(0, max(ram_values) * 1.15)

    fig.tight_layout()
    fig.savefig(output_path, dpi=100)
    plt.close(fig)

    return os.path.abspath(output_path)


def run_pipeline(output_dir: str = "assets/poc") -> dict[str, str]:
    """Execute the full metrics-to-chart pipeline.

    Args:
        output_dir: Directory to save generated charts.

    Returns:
        Dict mapping chart type to output file path.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    records = generate_fake_records()

    latency_path = os.path.join(output_dir, "latency_chart.png")
    memory_path = os.path.join(output_dir, "memory_chart.png")

    latency_result = generate_latency_bar_chart(records, latency_path)
    memory_result = generate_memory_bar_chart(records, memory_path)

    return {
        "latency": latency_result,
        "memory": memory_result,
    }


if __name__ == "__main__":
    results = run_pipeline()
    for chart_type, path in results.items():
        size = os.path.getsize(path)
        print(f"[OK] {chart_type}: {path} ({size} bytes)")
