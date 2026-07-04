"""GPU inference runner.

Delegates model loading and generation to a configured InferenceProvider,
collects timing and memory metrics via MetricsCollector, and returns a
MetricsRecord. Catches OOM errors and returns error status.

Per docs/INTERFACES.md §3 and docs/IMPLEMENTATION.md §5.2.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from airllm_benchmark.services.metrics import MetricsCollector, MetricsRecord

if TYPE_CHECKING:
    from airllm_benchmark.providers.base import InferenceProvider

GPU_MODE = "gpu_provider"
DEFAULT_DEVICE = "cuda"


class GpuRunner:
    """Execute inference on GPU via a configured provider.

    Delegates to an :class:`InferenceProvider` for model loading and
    text generation. Uses :class:`MetricsCollector` to track timing
    and memory usage. Catches CUDA OOM and other runtime errors.
    """

    def run(
        self,
        provider: InferenceProvider,
        model_id: str,
        prompt: str,
        max_tokens: int,
    ) -> MetricsRecord:
        """Execute one GPU inference run and return metrics.

        Lifecycle:
            1. Start metrics collection
            2. Load model onto GPU
            3. Mark load complete
            4. Generate text
            5. Stop metrics
            6. Unload model
            7. Return MetricsRecord

        Args:
            provider: Configured inference provider (e.g. Transformers).
            model_id: HuggingFace model identifier.
            prompt: Input text to complete.
            max_tokens: Maximum tokens to generate.

        Returns:
            MetricsRecord with timing, memory, and generation results.
        """
        collector = MetricsCollector()
        collector.start(
            model_id=model_id,
            mode=GPU_MODE,
            provider=type(provider).__name__.lower().replace("_provider", ""),
            prompt=prompt,
            prompt_id="",
            quantization="none",
            max_tokens=max_tokens,
        )

        try:
            provider.load_model(model_id, DEFAULT_DEVICE)
            collector.mark_load_complete()

            output = provider.generate(prompt, max_tokens)
            collector.stop()

            tokens = _estimate_tokens(output)
            return collector.get_record(
                tokens_generated=tokens,
                status="success",
                error="",
            )

        except Exception as exc:
            collector.stop()
            status, error_msg = _classify_error(exc)
            return collector.get_record(
                tokens_generated=0,
                status=status,
                error=error_msg,
            )

        finally:
            provider.unload()


def _estimate_tokens(text: str) -> int:
    """Estimate token count from generated text length.

    Uses rough 4-character-per-token heuristic. Sufficient for
    benchmarking purposes where exact token counts are less
    critical than relative comparisons.

    Args:
        text: Generated text output.

    Returns:
        Estimated number of tokens.
    """
    return max(1, len(text) // 4)


def _classify_error(exc: Exception) -> tuple[str, str]:
    """Classify exception into OOM or generic error.

    Args:
        exc: The caught exception.

    Returns:
        Tuple of (status, error_message). Status is "oom" for
        memory errors, "error" for all others.
    """
    msg = str(exc)
    if re.search(r"(out of memory|cuda.*oom|cublas.*oom)", msg, re.IGNORECASE):
        return "oom", msg
    return "error", msg
