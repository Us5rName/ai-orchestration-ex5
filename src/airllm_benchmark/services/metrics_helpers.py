"""Metrics record data and assembly helpers.

Separates the data contract (MetricsRecord) from the collection
service (MetricsCollector in metrics.py). Follows the same split
pattern as chart_helpers.py / table_helpers.py from the visualizer.

Per modular-design: Single Responsibility — data definition vs.
data collection.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from . import metrics_sampler as _sampler

if TYPE_CHECKING:
    from typing import Any


@dataclass(frozen=True)
class MetricsRecord:
    """Single metrics record from one inference run.

    Matches CONFIG.md §1 schema exactly.
    """

    run_id: str
    model: str
    mode: str
    provider: str
    prompt: str
    prompt_id: str
    quantization: str
    max_new_tokens: int
    load_time_s: float
    ttft_s: float
    total_runtime_s: float
    tokens_generated: int
    generation_throughput: float  # tokens/sec during generation phase
    peak_ram_mb: float
    peak_vram_mb: float
    status: str
    error: str
    timestamp: str


def assemble_record(
    collector_id: int,
    ctx: dict[str, Any],
    load_time: float,
    gen_start_time: float,
    first_token_time: float,
    start_time: float,
    stop_time: float,
    tokens_generated: int,
    peak_ram_mb: float,
    status: str,
    error: str,
) -> MetricsRecord:
    """Assemble a MetricsRecord from collector internals.

    Computes real TTFT (first-token latency) when the provider reported
    one via ``mark_first_token``, and calculates generation throughput
    from token count and generation duration.

    Args:
        collector_id: id() of the collector for run_id generation.
        ctx: Context dict stored by MetricsCollector.start().
        load_time: Finalized load_time_s value.
        gen_start_time: perf_counter value at generation start (0 if unset).
        first_token_time: perf_counter value when the first token was
            produced (0 if the provider never called mark_first_token).
        start_time: perf_counter value at collection start.
        stop_time: perf_counter value at collection stop.
        tokens_generated: Number of tokens produced.
        status: Run status (success, oom, timeout).
        error: Error message if status != success.

    Returns:
        MetricsRecord matching CONFIG.md §1 schema.
    """
    total = stop_time - start_time

    # TTFT = real time from generation start to first token produced.
    # Unmeasured (no per-token hook for this provider) -> 0.0, not an
    # approximation from load/setup time.
    ttft = (
        first_token_time - gen_start_time
        if first_token_time > 0 and gen_start_time > 0
        else 0.0
    )

    # Generation throughput = tokens / generation_duration.
    gen_duration = stop_time - gen_start_time
    throughput = tokens_generated / gen_duration if gen_start_time > 0 and gen_duration > 0 else 0.0

    return MetricsRecord(
        run_id=f"run_{collector_id:x}",
        model=ctx.get("model_id", ""),
        mode=ctx.get("mode", ""),
        provider=ctx.get("provider", ""),
        prompt=ctx.get("prompt", ""),
        prompt_id=ctx.get("prompt_id", ""),
        quantization=ctx.get("quantization", ""),
        max_new_tokens=int(ctx.get("max_tokens", 0)),
        load_time_s=round(load_time, 4),
        ttft_s=round(ttft, 4),
        total_runtime_s=round(total, 4),
        tokens_generated=tokens_generated,
        generation_throughput=round(throughput, 2),
        peak_ram_mb=round(peak_ram_mb, 2),
        peak_vram_mb=round(_sampler.VramTracker.peak_mb(), 2),
        status=status,
        error=error,
        timestamp=datetime.now(UTC).isoformat(),
    )
