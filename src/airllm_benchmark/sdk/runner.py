"""Inference runner protocol and runner manager.

Defines the :class:`InferenceRunner` protocol that all concrete runners must
implement.  Also provides :class:`RunnerManager` which lazily instantiates
and caches the appropriate runner for each inference mode (gpu_provider,
cpu_baseline, airllm).

Per docs/INTERFACES.md §3.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from airllm_benchmark.providers.base import InferenceProvider
    from airllm_benchmark.services.metrics import MetricsRecord


# ——— Protocol ———


class InferenceRunner(Protocol):
    """Interface for all inference runners.

    Each concrete runner (GPU, CPU, AirLLM) implements this protocol.
    The ``run`` method executes a single inference and returns a
    :class:`MetricsRecord` with timing, memory, and generation results.
    """

    def run(
        self,
        provider: InferenceProvider,
        model_id: str,
        prompt: str,
        max_tokens: int,
        quantization: str = "none",
    ) -> MetricsRecord:
        """Execute one inference run and return metrics.

        Args:
            provider: Loaded inference provider.
            model_id: HuggingFace model identifier.
            prompt: Input text to complete.
            max_tokens: Maximum tokens to generate.
            quantization: Quantization level ("4bit", "8bit", "none").

        Returns:
            MetricsRecord from this run.
        """
        ...


# ——— Runner Manager ———


class RunnerManager:
    """Selects and caches the correct runner for each inference mode.

    Lazily initializes GPU, CPU, and AirLLM runners on first access.
    Cached instances are reused for subsequent calls with the same mode.
    """

    def __init__(self) -> None:
        """Initialize manager with no runners (lazy initialization)."""
        self._gpu_runner: InferenceRunner | None = None
        self._cpu_runner: InferenceRunner | None = None
        self._airllm_runner: InferenceRunner | None = None

    def get_runner(self, mode: str) -> InferenceRunner:
        """Return the runner for the given inference mode.

        Args:
            mode: One of ``"gpu_provider"``, ``"cpu_baseline"``, ``"airllm"``.

        Returns:
            The InferenceRunner for the requested mode.

        Raises:
            ValueError: If *mode* is not a recognized inference mode.
        """
        if mode == "gpu_provider":
            if self._gpu_runner is None:
                from airllm_benchmark.sdk.gpu_runner import GpuRunner

                self._gpu_runner = GpuRunner()
            return self._gpu_runner

        if mode == "cpu_baseline":
            if self._cpu_runner is None:
                from airllm_benchmark.sdk.cpu_runner import CpuRunner

                self._cpu_runner = CpuRunner()
            return self._cpu_runner

        if mode == "airllm":
            if self._airllm_runner is None:
                from airllm_benchmark.sdk.airllm_runner import AirllmRunner

                self._airllm_runner = AirllmRunner()
            return self._airllm_runner

        valid = ", ".join(self.get_all_modes())
        msg = f"Unknown inference mode: '{mode}'. Must be one of: {valid}"
        raise ValueError(msg)

    def get_all_modes(self) -> list[str]:
        """Return the list of supported inference modes.

        Returns:
            List of mode strings: gpu_provider, cpu_baseline, airllm.
        """
        return ["gpu_provider", "cpu_baseline", "airllm"]
