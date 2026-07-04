"""AirLLM paged inference runner.

Built-in runner that uses AirLLM's on-demand weight loading to run
models larger than available RAM. Unlike GPU/CPU runners, this does
not delegate to an external provider — it loads and generates directly
via `airllm.AutoModel`.

Per docs/INTERFACES.md §3 and docs/TODO.md task 5.4.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from airllm_benchmark.services.metrics import MetricsCollector, MetricsRecord

from .airllm_generator import generate_text
from .airllm_loader import load_model

if TYPE_CHECKING:
    from airllm_benchmark.providers.base import InferenceProvider

AIRLLM_MODE = "airllm"
AIRLLM_PROVIDER = "airllm"


class AirllmRunner:
    """Execute inference via AirLLM paged inference.

    Loads the model directly through ``airllm.AutoModel`` with
    optional quantization. Does not delegate to an external
    provider — AirLLM handles weight paging internally.
    """

    def run(
        self,
        provider: InferenceProvider | None,
        model_id: str,
        prompt: str,
        max_tokens: int,
        quantization: str = "none",
    ) -> MetricsRecord:
        """Execute one AirLLM inference run and return metrics.

        Lifecycle:
            1. Start metrics collection
            2. Load model via AirLLM (paged, on-demand weights)
            3. Mark generation start (TTFT boundary)
            4. Generate text (returns real token count)
            5. Stop metrics
            6. Return MetricsRecord

        Args:
            provider: Unused — AirLLM is builtin. Accepted for
                protocol compliance; pass ``None``.
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
            mode=AIRLLM_MODE,
            provider=AIRLLM_PROVIDER,
            prompt=prompt,
            prompt_id="",
            quantization=quantization,
            max_tokens=max_tokens,
        )

        try:
            model = load_model(model_id, quantization)
            collector.mark_load_complete()

            collector.mark_generation_start()
            output, tokens = generate_text(model, prompt, max_tokens)
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


def _classify_error(exc: Exception) -> tuple[str, str]:
    """Classify exception into OOM or generic error.

    Args:
        exc: The caught exception.

    Returns:
        Tuple of (status, error_message). Status is "oom" for
        memory errors, "error" for all others.
    """
    if isinstance(exc, MemoryError):
        return "oom", str(exc)
    return "error", str(exc)
