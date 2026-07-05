"""Hardware-aware narrative summary for the reporting layer (§5.3).

Split from report_builder.py to stay under the 150-line limit.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from airllm_benchmark.shared.config_models import HardwareConfig

    from .metrics import MetricsRecord


def build_narrative_summary(
    records: list[MetricsRecord],
    hardware: HardwareConfig,
    tier_lookup: Callable[[str], str],
) -> str:
    """Build the hardware-aware narrative summary (§5.3).

    Args:
        records: Metrics records to summarize.
        hardware: Loaded hardware config (cpu/gpu/ram_gb/os).
        tier_lookup: Callable mapping a model id to its tier name.

    Returns:
        Multi-section narrative text.
    """
    if not records:
        return "No records to summarize."

    lines: list[str] = ["Hardware"]
    lines.append(
        f"  CPU: {hardware.cpu} | GPU: {hardware.gpu} | RAM: {hardware.ram_gb} GB | OS: {hardware.os}"
    )

    successful = [r for r in records if r.status == "success"]
    lines.append("\nKey Findings")
    if successful:
        fastest = min(successful, key=lambda r: r.total_runtime_s)
        peak_mem = max(records, key=lambda r: r.peak_ram_mb)
        lines.append(
            f"  Fastest: {fastest.mode} on {tier_lookup(fastest.model)} tier "
            f"({fastest.total_runtime_s:.2f}s)"
        )
        lines.append(
            f"  Highest peak RAM: {peak_mem.mode} on {tier_lookup(peak_mem.model)} tier "
            f"({peak_mem.peak_ram_mb:.0f} MB)"
        )
    else:
        lines.append("  No successful runs.")

    lines.extend(_airllm_tradeoff_lines(records))
    lines.extend(_anomaly_lines(records))

    return "\n".join(lines)


def _airllm_tradeoff_lines(records: list[MetricsRecord]) -> list[str]:
    """Build the AirLLM vs cpu_baseline trade-off section."""
    lines = ["\nAirLLM Trade-off"]
    airllm = [r for r in records if r.mode == "airllm" and r.status == "success"]
    cpu_baseline = [r for r in records if r.mode == "cpu_baseline"]
    cpu_success = [r for r in cpu_baseline if r.status == "success"]

    if airllm and cpu_success:
        avg_airllm = sum(r.total_runtime_s for r in airllm) / len(airllm)
        avg_cpu = sum(r.total_runtime_s for r in cpu_success) / len(cpu_success)
        ratio = avg_airllm / avg_cpu if avg_cpu > 0 else float("nan")
        lines.append(f"  AirLLM/CPU runtime ratio: {ratio:.2f}x")
    if airllm and cpu_baseline and not cpu_success:
        lines.append("  AirLLM succeeded where cpu_baseline failed (OOM/timeout).")
    if not airllm:
        lines.append("  No successful AirLLM runs to compare.")

    return lines


def _anomaly_lines(records: list[MetricsRecord]) -> list[str]:
    """Build the anomalies section: failures, zero VRAM, empty prompt_id."""
    lines = ["\nAnomalies"]
    anomalies = [
        r for r in records if r.status != "success" or r.peak_vram_mb == 0.0 or r.prompt_id == ""
    ]
    if not anomalies:
        lines.append("  None detected.")
        return lines

    for r in anomalies:
        reason = r.error or ("zero VRAM" if r.peak_vram_mb == 0.0 else "empty prompt_id")
        lines.append(f"  {r.run_id} ({r.mode}, {r.model}): {reason}")
    return lines
