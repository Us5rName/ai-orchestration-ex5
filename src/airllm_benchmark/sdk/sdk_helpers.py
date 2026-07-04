"""Helper functions for BenchmarkSDK.

Delegates provider factory, benchmark orchestration, and visualization
rendering so sdk.py stays within the 150-line limit.
Per PLAN.md C3 — SDK orchestrates runners, writer, and visualizer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from airllm_benchmark.providers.transformers_provider import TransformersProvider
from airllm_benchmark.sdk.runner import RunnerManager
from airllm_benchmark.sdk.sdk_summary import build_summary
from airllm_benchmark.services.result_writer import ResultWriter
from airllm_benchmark.services.visualizer import VisualizationResult
from airllm_benchmark.shared.config_loader import validate_config

if TYPE_CHECKING:
    from collections.abc import Sequence

    from airllm_benchmark.providers.base import InferenceProvider
    from airllm_benchmark.services.metrics import MetricsRecord
    from airllm_benchmark.services.visualizer import Visualizer
    from airllm_benchmark.shared.config_models import ExperimentConfig

__all__ = [
    "build_summary",
    "create_provider",
    "render_visualization",
    "resolve_model_id",
    "validate_config",
]


def resolve_model_id(config: ExperimentConfig, model_name: str) -> str:
    """Resolve a model tier name to its HuggingFace model ID.

    If the model name is already a full HuggingFace identifier (contains
    a slash), return it unchanged. Otherwise look it up in the config.

    Args:
        config: Loaded experiment configuration.
        model_name: Tier name (e.g. ``"small"``) or full model ID.

    Returns:
        HuggingFace model identifier string.

    Raises:
        KeyError: If tier name is not found in config.
    """
    if "/" in model_name:
        return model_name
    return config.get_model_id(model_name)


def create_provider(
    name: str, provider_config: dict, quantization: str = "none"
) -> InferenceProvider:
    """Instantiate an InferenceProvider by name.

    Args:
        name: Provider identifier (e.g. ``"transformers"``).
        provider_config: Per-provider configuration from experiment.json.
        quantization: Quantization level (``"4bit"``, ``"8bit"``, ``"none"``).

    Returns:
        Configured InferenceProvider instance.

    Raises:
        ValueError: If *name* is not a registered provider.
    """
    cfg = provider_config.get(name, {})

    if name == "transformers":
        device = cfg.get("device", "cpu")
        return TransformersProvider(device=device, quantization=quantization)

    msg = f"Unsupported provider: '{name}'. Available: transformers"
    raise ValueError(msg)


def _run_benchmark_impl(
    config: ExperimentConfig,
    runner_mgr: RunnerManager,
    writer: ResultWriter,
) -> list[MetricsRecord]:
    """Execute full benchmark matrix and persist results incrementally."""
    records: list[MetricsRecord] = []

    for model_name in config.models:
        model_id = config.get_model_id(model_name)
        for mode in runner_mgr.get_all_modes():
            for prompt_id in config.prompts:
                prompt = config.get_prompt(prompt_id)

                # AirLLM is builtin — no external provider needed.
                if mode == "airllm":
                    from airllm_benchmark.sdk.airllm_runner import AirllmRunner

                    airllm_runner = AirllmRunner()
                    record = airllm_runner.run(
                        provider=None,
                        model_id=model_id,
                        prompt=prompt,
                        max_tokens=config.max_new_tokens,
                        quantization=config.quantization,
                    )
                else:
                    provider_name = _resolve_provider(config, mode)
                    provider = create_provider(
                        provider_name, config.provider_config, config.quantization
                    )
                    runner = runner_mgr.get_runner(mode)
                    record = runner.run(
                        provider=provider,
                        model_id=model_id,
                        prompt=prompt,
                        max_tokens=config.max_new_tokens,
                        quantization=config.quantization,
                    )

                writer.append(record)
                records.append(record)

    return records


def render_visualization(
    visualizer: Visualizer, records: Sequence[MetricsRecord], output_dir: str
) -> VisualizationResult:
    """Generate charts and a comparison table for the given records."""
    chart_paths = visualizer.generate_all(list(records), output_dir)
    table_text = visualizer.generate_table(list(records))
    return VisualizationResult(chart_paths=chart_paths, table_text=table_text)


def _resolve_provider(config: ExperimentConfig, mode: str) -> str:
    """Return the provider name for the given inference mode."""
    if mode == "gpu_provider":
        return config.gpu_provider
    if mode == "cpu_baseline":
        return config.cpu_baseline_provider
    if mode == "airllm":
        return "airllm"

    msg = f"No provider mapping for mode: '{mode}'"
    raise ValueError(msg)
