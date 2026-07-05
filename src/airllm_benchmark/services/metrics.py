"""Metrics collection for inference benchmarking.

Tracks timing, RAM, and VRAM during a single inference run.
Per INTERFACES.md §4-§5.

Separation of concerns:
    - MetricsRecord (data contract) lives in metrics_helpers.py
    - MetricsCollector (service) lives here
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from . import metrics_helpers as _helpers
from . import metrics_sampler as _sampler
from .metrics_helpers import MetricsRecord

if TYPE_CHECKING:
    from typing import Any


class MetricsCollector:
    """Collects timing, RAM, and VRAM metrics for one inference run.

    Usage:
        c = MetricsCollector()
        c.start(model_id, mode, provider, prompt, pid, quant, max_tok)
        c.mark_download_complete()   # optional — separate download from transfer
        c.mark_load_complete()
        c.mark_generation_start()    # generation phase boundary
        # ... generate (provider may call c.mark_first_token() on token 1) ...
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
        self._download_time: float = 0.0
        self._load_time: float = 0.0
        self._gen_start_time: float = 0.0
        self._first_token_time: float = 0.0
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
        self._download_time = 0.0
        self._load_time = 0.0
        self._gen_start_time = 0.0
        self._first_token_time = 0.0
        self._stop_time = 0.0
        _sampler.VramTracker.reset()
        self._ram.start()

    def mark_download_complete(self) -> None:
        """Mark HF download complete. Separates download from GPU transfer."""
        self._download_time = time.perf_counter() - self._start_time

    def mark_load_complete(self) -> None:
        """Mark model loading as complete. Captures load_time_s.

        If mark_download_complete was called, load_time_s = transfer only.
        Otherwise load_time_s = total time since start (includes download).
        """
        if self._download_time > 0:
            self._load_time = time.perf_counter() - (self._start_time + self._download_time)
        else:
            self._load_time = time.perf_counter() - self._start_time

    def mark_generation_start(self) -> None:
        """Mark generation start. Used as the TTFT/throughput reference point."""
        self._gen_start_time = time.perf_counter()

    def mark_first_token(self) -> None:
        """Mark the moment the first generated token is produced.

        Called by providers that support per-token callbacks (currently
        only TransformersProvider, via its optional ``_on_first_token``
        hook). If never called, ``ttft_s`` falls back to 0.0 — real
        first-token latency is simply unmeasured for that provider,
        rather than being approximated from load/setup time.
        """
        if self._first_token_time == 0.0:
            self._first_token_time = time.perf_counter()

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

        Delegates to :func:`metrics_helpers.assemble_record` which
        computes TTFT and generation throughput from internal timers.

        Args:
            tokens_generated: Number of tokens produced.
            status: Run status (success, oom, timeout).
            error: Error message if status != success.

        Returns:
            MetricsRecord matching CONFIG.md §1 schema.
        """
        return _helpers.assemble_record(
            collector_id=id(self),
            ctx=self._ctx,
            load_time=self._load_time,
            gen_start_time=self._gen_start_time,
            first_token_time=self._first_token_time,
            start_time=self._start_time,
            stop_time=self._stop_time,
            tokens_generated=tokens_generated,
            peak_ram_mb=self._ram.peak_mb(),
            status=status,
            error=error,
        )
