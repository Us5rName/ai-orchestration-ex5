"""Pre-benchmark validation — config, provider, and model-cache checks.

Implements docs/TODO.md task 7.4: verify the benchmark is configured
correctly *before* any expensive inference run. Loads and validates
config, confirms each configured provider constructs cleanly, and
reports (informationally) whether models are already HF-cached.
Never loads model weights and never calls ``generate()``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from airllm_benchmark.shared.cache_check import model_cache_status
from airllm_benchmark.shared.config_loader import (
    load_experiment,
    load_hardware,
    validate_hardware,
)

from . import sdk_helpers as _helpers

if TYPE_CHECKING:
    from pathlib import Path

    from airllm_benchmark.shared.config_models import ExperimentConfig


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of a pre-benchmark validation dry-run.

    Input:  Loaded config + provider construction attempts + cache scan.
    Output: Structured pass/fail per check plus human-readable detail.
    Setup:  Produced by ``run_validation()``; never constructed directly
        by callers other than the SDK.
    """

    config_ok: bool
    config_error: str
    providers: dict[str, bool] = field(default_factory=dict)
    provider_errors: dict[str, str] = field(default_factory=dict)
    models_cached: dict[str, bool] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """True if config is valid and every provider constructed cleanly.

        Model-cache status is informational only per task 7.4's Definition
        of Done — a missing cache entry does not fail validation because
        network access can fill it in at run time.
        """
        return self.config_ok and all(self.providers.values())


def run_validation(config_dir: Path | None = None) -> ValidationResult:
    """Run the full pre-benchmark validation dry-run. Executes no inference.

    Args:
        config_dir: Optional config directory override.

    Returns:
        ValidationResult summarizing config, provider, and cache checks.
    """
    config_ok, config_error = _check_config(config_dir)
    if not config_ok:
        return ValidationResult(config_ok=False, config_error=config_error)

    experiment = load_experiment(config_dir)
    providers, provider_errors = _check_providers(experiment)
    model_ids = [experiment.get_model_id(name) for name in experiment.models]

    return ValidationResult(
        config_ok=True,
        config_error="",
        providers=providers,
        provider_errors=provider_errors,
        models_cached=model_cache_status(model_ids),
    )


def _check_config(config_dir: Path | None) -> tuple[bool, str]:
    """Load and validate experiment + hardware config; never raises."""
    try:
        load_experiment(config_dir)
        validate_hardware(load_hardware(config_dir))
    except (FileNotFoundError, ValueError) as exc:
        return False, str(exc)
    return True, ""


def _check_providers(experiment: ExperimentConfig) -> tuple[dict[str, bool], dict[str, str]]:
    """Instantiate each configured provider without loading model weights."""
    names = {experiment.gpu_provider, experiment.cpu_baseline_provider}
    ok: dict[str, bool] = {}
    errors: dict[str, str] = {}
    for name in names:
        try:
            _helpers.create_provider(name, experiment.provider_config, "none")
            ok[name] = True
        except Exception as exc:  # noqa: BLE001 - report any construction failure
            ok[name] = False
            errors[name] = str(exc)
    return ok, errors
