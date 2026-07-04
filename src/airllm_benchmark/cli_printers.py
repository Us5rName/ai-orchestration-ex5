"""CLI output formatting for AirLLM Benchmark.

Extracted from main.py to respect the 150-line file limit.
Handles all stdout formatting for single-run and full-benchmark results.
"""

from __future__ import annotations

from airllm_benchmark.services.metrics import MetricsRecord


def print_result(record: MetricsRecord) -> None:
    """Print formatted metrics result for a single inference run."""
    sep = "=" * 60
    sub = "  " + "-" * 40
    icon = "✓" if record.status == "success" else "✗"

    print(sep)
    print("  Inference Result")
    print(sep)
    print(f"  Model:        {record.model}")
    print(f"  Mode:         {record.mode}")
    print(f"  Provider:     {record.provider}")
    print(f"  Quantization: {record.quantization}")
    print(f"  Prompt:       {record.prompt}")
    print()
    print("  Timing")
    print(sub)
    print(f"  Load time:       {record.load_time_s:.2f}s")
    print(f"  TTFT:            {record.ttft_s:.2f}s")
    print(f"  Total runtime:   {record.total_runtime_s:.2f}s")
    print()
    print("  Generation")
    print(sub)
    print(f"  Max new tokens:  {record.max_new_tokens}")
    print(f"  Tokens generated:{record.tokens_generated}")
    print(f"  Throughput:      {record.generation_throughput:.1f} tok/s")
    print()
    print("  Memory")
    print(sub)
    print(f"  Peak RAM:  {record.peak_ram_mb:.0f} MB")
    if record.peak_vram_mb > 0:
        print(f"  Peak VRAM: {record.peak_vram_mb:.0f} MB")
    print()
    print(f"  Status:  {icon} {record.status}")
    if record.error:
        print(f"  Error:   {record.error}")
    print()
    print(f"  Timestamp: {record.timestamp}")
    print(sep)


def print_run_all_result(result: dict) -> None:
    """Print formatted benchmark summary from sdk.run_benchmark().

    Args:
        result: Dict with keys summary, chart_paths, table_text
            (per INTERFACES.md §1).
    """
    sep = "=" * 60
    print(sep)
    print("  Benchmark Complete")
    print(sep)
    print(result["summary"])
    print()
    print(result["table_text"])
    if result["chart_paths"]:
        paths = ", ".join(result["chart_paths"])
        print(f"\nCharts: {paths}")
    print(sep)
