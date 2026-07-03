"""Metrics Record Assembly PoC — Assemble a metrics record from timing + peak data.

Proves a full metrics record matching CONFIG.md §1 can be constructed
before building the full metrics module.

Run:
    uv run python pocs/metrics_record_poc.py
"""

from __future__ import annotations

import time
from typing import Any

from pocs.metrics_peak_poc import PeakResult
from pocs.metrics_timing_poc import TimingResult


def poc_assemble_record(
    timing: TimingResult,
    peak: PeakResult,
    model_id: str,
    mode: str,
    prompt: str,
    prompt_id: str,
    max_tokens: int,
    tokens_generated: int,
    status: str,
) -> dict[str, Any]:
    """Prove a metrics record can be assembled from timing + peak data.

    Matches the Metrics Record schema from CONFIG.md §1.

    Args:
        timing: Timing result from poc_timing.
        peak: Peak result from poc_peak_calculation.
        model_id: HuggingFace model identifier.
        mode: Inference mode (gpu_provider, cpu_baseline, airllm).
        prompt: Input prompt text.
        prompt_id: Prompt identifier (P1, P2, P3).
        max_tokens: Token generation limit.
        tokens_generated: Number of tokens produced.
        status: Run status (success, oom, timeout).

    Returns:
        Dict matching Metrics Record schema.
    """
    return {
        "run_id": "poc_run_001",
        "model": model_id,
        "mode": mode,
        "provider": "transformers",
        "prompt": prompt,
        "prompt_id": prompt_id,
        "quantization": "none",
        "max_new_tokens": max_tokens,
        "load_time_s": 0.0,
        "ttft_s": timing.elapsed_seconds,
        "total_runtime_s": timing.elapsed_seconds,
        "tokens_generated": tokens_generated,
        "peak_ram_mb": peak.peak_rss_mb,
        "peak_vram_mb": 0.0,
        "status": status,
        "error": "",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
    }


if __name__ == "__main__":
    from pocs.metrics_peak_poc import poc_peak_calculation
    from pocs.metrics_sampling_poc import MemorySample
    from pocs.metrics_timing_poc import poc_timing

    timing = poc_timing()
    peak = poc_peak_calculation([MemorySample(timestamp=0.0, rss_mb=128.5)])
    record = poc_assemble_record(
        timing=timing,
        peak=peak,
        model_id="test/model",
        mode="cpu_baseline",
        prompt="Hello world",
        prompt_id="P1",
        max_tokens=32,
        tokens_generated=10,
        status="success",
    )
    print(f"Record keys: {sorted(record.keys())}")
