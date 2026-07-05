"""GPU inference runner.

Delegates model loading and generation to a configured InferenceProvider,
collects timing and memory metrics via MetricsCollector, and returns a
MetricsRecord. Catches OOM errors and returns error status.

Per docs/INTERFACES.md §3 and docs/IMPLEMENTATION.md §5.2.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, cast

from airllm_benchmark.services.metrics import MetricsCollector, MetricsRecord

if TYPE_CHECKING:
    from airllm_benchmark.providers.base import InferenceProvider

GPU_MODE = "gpu_provider"


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
        quantization: str = "none",
    ) -> MetricsRecord:
        """Execute one GPU inference run and return metrics.

        Lifecycle:
            1. Start metrics collection
            2. Load model onto GPU (marks download + load complete)
            3. Mark generation start (TTFT boundary)
            4. Generate text (returns real token count)
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
            provider=_provider_name(provider),
            prompt=prompt,
            prompt_id="",
            quantization=quantization,
            max_tokens=max_tokens,
        )

        try:
            # Wire download callback so mark_download_complete fires during
            # load_model, not after — separating HF download from GPU transfer.
            if hasattr(provider, "_on_download_complete"):
                # Only TransformersProvider exposes this callback.
                # Cast to Any to satisfy static type checker.
                cast(Any, provider)._on_download_complete = collector.mark_download_complete
            if hasattr(provider, "_on_first_token"):
                # Real TTFT — only providers with a per-token hook support this.
                cast(Any, provider)._on_first_token = collector.mark_first_token

            # Pass None (not a hardcoded device) so providers that accept it,
            # e.g. TransformersProvider, fall back to their own constructed
            # device instead of always being forced onto GPU.
            provider.load_model(model_id, None)
            collector.mark_load_complete()

            collector.mark_generation_start()
            output, tokens = provider.generate(prompt, max_tokens)
            collector.stop()

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


def _provider_name(provider: InferenceProvider) -> str:
    """Extract short provider name from class name.

    Strips the trailing \"Provider\" suffix so TransformersProvider
    becomes \"transformers\", OllamaProvider becomes \"ollama\", etc.

    Args:
        provider: An InferenceProvider instance.

    Returns:
        Lowercase provider name without suffix.
    """
    name = type(provider).__name__.lower()
    if name.endswith("provider"):
        name = name[: -len("provider")]
    return name
