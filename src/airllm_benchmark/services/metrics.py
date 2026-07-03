"""Metrics collection for inference benchmarking.

Tracks timing, RAM, and VRAM during a single inference run.
Per INTERFACES.md §4-§5.
"""

from __future__ import annotations

import time
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
    peak_ram_mb: float
    peak_vram_mb: float
    status: str
    error: str
    timestamp: str


class MetricsCollector:
    """Collects timing, RAM, and VRAM metrics for one inference run.

    Usage:
        c = MetricsCollector()
        c.start(model_id, mode, provider, prompt, pid, quant, max_tok)
        c.mark_load_complete()
        # ... generate ...
        c.stop()
        record = c.get_record(tokens, status, error)
    """

    def __init__(self, sampling_interval: float = 1.0) -> None:
        """Init collector.

        Args:
            sampling_interval: Seconds between RAM samples.
        """
        self._ram = _sampler.RamSampler(interval=sampling_interval)
        self._start_time: float = 0.0
        self._load_time: float = 0.0
        self._stop_time: float = 0.0
        self._ctx: dict[str, Any] = {}

    def start(
        self,
        model_id: str,
        mode: str,
        provider: str,
        prompt: str,
        prompt_id: str,
        quantization: str,
        max_tokens: int,
    ) -> None:
        """Start timing and memory sampling. Store runner context."""
        self._ctx = {
            "model_id": model_id,
            "mode": mode,
            "provider": provider,
            "prompt": prompt,
            "prompt_id": prompt_id,
            "quantization": quantization,
            "max_tokens": max_tokens,
        }
        self._start_time = time.perf_counter()
        self._load_time = 0.0
        self._stop_time = 0.0
        _sampler.VramTracker.reset()
        self._ram.start()

    def mark_load_complete(self) -> None:
        """Mark model loading as complete. Captures load_time_s."""
        self._load_time = time.perf_counter() - self._start_time

    def stop(self) -> None:
        """Stop memory sampling and finalize timing."""
        self._stop_time = time.perf_counter()
        self._ram.stop()

    def get_record(
        self,
        tokens_generated: int,
        status: str,
        error: str = "",
    ) -> MetricsRecord:
        """Assemble metrics record from stored context + results.

        Args:
            tokens_generated: Number of tokens produced.
            status: Run status (success, oom, timeout).
            error: Error message if status != success.

        Returns:
            MetricsRecord matching CONFIG.md §1 schema.
        """
        total = self._stop_time - self._start_time
        return MetricsRecord(
            run_id=f"run_{id(self):x}",
            model=self._ctx.get("model_id", ""),
            mode=self._ctx.get("mode", ""),
            provider=self._ctx.get("provider", ""),
            prompt=self._ctx.get("prompt", ""),
            prompt_id=self._ctx.get("prompt_id", ""),
            quantization=self._ctx.get("quantization", ""),
            max_new_tokens=int(self._ctx.get("max_tokens", 0)),
            load_time_s=round(self._load_time, 4),
            ttft_s=round(self._load_time, 4),
            total_runtime_s=round(total, 4),
            tokens_generated=tokens_generated,
            peak_ram_mb=round(self._ram.peak_mb(), 2),
            peak_vram_mb=round(_sampler.VramTracker.peak_mb(), 2),
            status=status,
            error=error,
            timestamp=datetime.now(UTC).isoformat(),
        )
