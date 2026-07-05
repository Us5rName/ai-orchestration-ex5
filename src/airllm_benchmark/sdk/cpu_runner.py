"""CPU baseline inference runner.

Delegates model loading and generation to a configured InferenceProvider
running on CPU. Collects timing and memory metrics via MetricsCollector
and returns a MetricsRecord. Catches MemoryError (RAM OOM) and other
runtime errors.

Unlike GpuRunner, this targets CPU devices and detects RAM-based OOM
instead of CUDA OOM. Large models may cause extreme memory pressure
or timeouts on CPU.

Per docs/INTERFACES.md §3 and docs/TODO.md task 5.3.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from airllm_benchmark.services.metrics import MetricsCollector, MetricsRecord

if TYPE_CHECKING:
    from airllm_benchmark.providers.base import InferenceProvider

CPU_MODE = "cpu_baseline"
DEFAULT_DEVICE = "cpu"


class CpuRunner:
    """Execute inference on CPU via a configured provider.

    Delegates to an :class:`InferenceProvider` for model loading and
    text generation on CPU. Uses :class:`MetricsCollector` to track
    timing and RAM usage. Catches MemoryError (RAM OOM) and other
    runtime errors.

    Unlike :class:`GpuRunner`, this targets CPU and detects RAM-based
    OOM instead of CUDA OOM. Large models on CPU may cause extreme
    memory pressure or very slow inference.
    """

    def run(
        self,
        provider: InferenceProvider,
        model_id: str,
        prompt: str,
        max_tokens: int,
        quantization: str = "none",
    ) -> MetricsRecord:
        """Execute one CPU inference run and return metrics.

        Lifecycle:
            1. Start metrics collection
            2. Load model onto CPU (marks load complete)
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
            quantization: Quantization level ("4bit", "8bit", "none").

        Returns:
            MetricsRecord with timing, RAM, and generation results.
        """
        collector = MetricsCollector()
        collector.start(
            model_id=model_id,
            mode=CPU_MODE,
            provider=_provider_name(provider),
            prompt=prompt,
            prompt_id="",
            quantization=quantization,
            max_tokens=max_tokens,
        )

        try:
            if hasattr(provider, "_on_first_token"):
                # Real TTFT — only providers with a per-token hook support this.
                cast(Any, provider)._on_first_token = collector.mark_first_token

            provider.load_model(model_id, DEFAULT_DEVICE)
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

    Detects RAM-based OOM (MemoryError) and patterns that indicate
    memory exhaustion. Returns "oom" for memory errors, "error"
    for all other exceptions.

    Args:
        exc: The caught exception.

    Returns:
        Tuple of (status, error_message). Status is "oom" for
        memory errors, "error" for all others.
    """
    if isinstance(exc, MemoryError):
        return "oom", str(exc)
    return "error", str(exc)


def _provider_name(provider: InferenceProvider) -> str:
    """Extract short provider name from class name.

    Strips the trailing "Provider" suffix so TransformersProvider
    becomes "transformers", OllamaProvider becomes "ollama", etc.

    Args:
        provider: An InferenceProvider instance.

    Returns:
        Lowercase provider name without suffix.
    """
    name = type(provider).__name__.lower()
    if name.endswith("provider"):
        name = name[: -len("provider")]
    return name
