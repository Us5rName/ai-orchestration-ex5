"""Helper functions for BenchmarkSDK.

Delegates provider factory and benchmark orchestration logic so
sdk.py stays within the 150-line limit.  Each function has a single
responsibility: create_provider instantiates providers from config,
and _run_benchmark_impl executes the full model×mode×prompt matrix.

Per PLAN.md C3 — SDK orchestrates runners, writer, and visualizer.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from airllm_benchmark.providers.transformers_provider import TransformersProvider
from airllm_benchmark.sdk.runner import RunnerManager
from airllm_benchmark.services.result_writer import ResultWriter
from airllm_benchmark.shared.config import load_experiment, load_hardware, validate_hardware

if TYPE_CHECKING:
    from collections.abc import Sequence

    from airllm_benchmark.providers.base import InferenceProvider
    from airllm_benchmark.services.metrics import MetricsRecord
    from airllm_benchmark.shared.config_models import ExperimentConfig


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


def create_provider(name: str, provider_config: dict) -> InferenceProvider:
    """Instantiate an InferenceProvider by name.

    Args:
        name: Provider identifier (e.g. ``"transformers"``).
        provider_config: Per-provider configuration from experiment.json.

    Returns:
        Configured InferenceProvider instance.

    Raises:
        ValueError: If *name* is not a registered provider.
    """
    cfg = provider_config.get(name, {})

    if name == "transformers":
        device = cfg.get("device", "cpu")
        return TransformersProvider(device=device)

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
            provider_name = _resolve_provider(config, mode)
            provider = create_provider(provider_name, config.provider_config)
            runner = runner_mgr.get_runner(mode)

            for prompt_id in config.prompts:
                prompt = config.get_prompt(prompt_id)
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


def build_summary(records: Sequence[MetricsRecord]) -> str:
    """Build human-readable summary grouped by mode."""
    lines: list[str] = [f"Benchmark Summary — {len(records)} runs total"]
    lines.append("-" * 40)

    modes = {"gpu_provider": [], "cpu_baseline": [], "airllm": []}
    for rec in records:
        if rec.mode in modes:
            modes[rec.mode].append(rec)

    for mode, recs in modes.items():
        if not recs:
            continue
        success = sum(1 for r in recs if r.status == "success")
        avg_runtime = sum(r.total_runtime_s for r in recs) / len(recs)
        lines.append(
            f"  {mode}: {len(recs)} runs, {success}/{len(recs)} success, avg {avg_runtime:.2f}s"
        )

    return "\n".join(lines)


def validate_config(config_dir: Path | None) -> None:
    """Validate experiment + hardware configs are loadable."""
    load_experiment(config_dir)
    hw = load_hardware(config_dir)
    validate_hardware(hw)
