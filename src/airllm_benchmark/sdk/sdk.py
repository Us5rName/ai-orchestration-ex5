"""BenchmarkSDK — single entry point for all benchmark operations.

CLI and any external consumer delegate here.  All business logic
flows through this class per ADR-001 (SDK-First Architecture).

Per docs/INTERFACES.md §1 and PLAN.md C3 Component Diagram.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from airllm_benchmark.sdk.runner import RunnerManager
from airllm_benchmark.services.metrics import MetricsRecord
from airllm_benchmark.services.result_writer import ResultWriter
from airllm_benchmark.services.visualizer import VisualizationResult, Visualizer
from airllm_benchmark.shared.config import (
    load_experiment,
    load_hardware,
    validate_hardware,
)

from . import sdk_helpers as _helpers

if TYPE_CHECKING:
    from collections.abc import Sequence


class BenchmarkSDK:
    """Single entry point for all benchmark operations.

    Orchestrates the full benchmark pipeline: config loading, runner
    dispatch, result persistence, and visualization generation.

    Per INTERFACES.md §1.
    """

    def __init__(self, config_dir: Path | str | None = None) -> None:
        """Initialize SDK with optional config directory override."""
        self._config_dir = Path(config_dir) if config_dir else None
        self._runner_mgr = RunnerManager()
        self._visualizer = Visualizer()

    # ——— INTERFACES.md §1: run_benchmark ———

    def run_benchmark(self) -> dict:
        """Execute full benchmark pipeline across all modes.

        Lifecycle:
            1. Load and validate config
            2. Clear previous results
            3. Run every (model, mode, prompt) combination
            4. Persist each result via ResultWriter
            5. Generate visualizations
            6. Return summary dict

        Returns:
            dict with keys: summary, chart_paths, table_text
        """
        config = load_experiment(self._config_dir)
        hw = load_hardware(self._config_dir)
        validate_hardware(hw)

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path("results") / f"metrics_{now}.json"
        writer = ResultWriter(str(output_path))
        writer.clear()

        records = _helpers._run_benchmark_impl(config, self._runner_mgr, writer)

        output_dir = str(Path("assets") / f"run_{now}")
        chart_paths = self._visualizer.generate_all(records, output_dir)
        table_text = self._visualizer.generate_table(records)

        return {
            "summary": _helpers.build_summary(records),
            "chart_paths": chart_paths,
            "table_text": table_text,
        }

    # ——— INTERFACES.md §1: run_single ———

    def run_single(
        self,
        model_id: str,
        mode: str,
        prompt: str,
        provider: str | None = None,
        quantization: str = "none",
    ) -> MetricsRecord:
        """Run a single inference and return metrics.

        Args:
            model_id: HuggingFace model identifier.
            mode: One of ``"gpu_provider"``, ``"cpu_baseline"``, ``"airllm"``.
            prompt: Input text to complete.
            provider: Inference provider name (default from config).
            quantization: Quantization level (``"4bit"``, ``"8bit"``, ``"none"``).

        Returns:
            MetricsRecord from this run.
        """
        config = load_experiment(self._config_dir)
        model_id = _helpers.resolve_model_id(config, model_id)

        # AirLLM is builtin — no external provider needed.
        if mode == "airllm":
            from airllm_benchmark.sdk.airllm_runner import AirllmRunner

            airllm_runner = AirllmRunner()
            return airllm_runner.run(
                provider=None,
                model_id=model_id,
                prompt=prompt,
                max_tokens=config.max_new_tokens,
                quantization=quantization,
            )

        provider_name = provider or _helpers._resolve_provider(config, mode)
        prov = _helpers.create_provider(provider_name, config.provider_config, quantization)
        runner = self._runner_mgr.get_runner(mode)

        return runner.run(
            provider=prov,
            model_id=model_id,
            prompt=prompt,
            max_tokens=config.max_new_tokens,
            quantization=quantization,
        )

    # ——— INTERFACES.md §1: generate_visualization ———

    def generate_visualization(
        self,
        records: Sequence[MetricsRecord],
        output_dir: str = "assets",
    ) -> VisualizationResult:
        """Generate charts and tables from metrics records.

        Args:
            records: List of metrics records to visualize.
            output_dir: Directory to save chart PNGs.

        Returns:
            VisualizationResult with chart_paths and table_text.
        """
        return _helpers.render_visualization(self._visualizer, records, output_dir)
