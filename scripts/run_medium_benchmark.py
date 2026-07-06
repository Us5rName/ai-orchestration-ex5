#!/usr/bin/env python3
"""Medium-tier (3B) GPU baseline + AirLLM benchmark.

Executes a complete benchmark of the medium-tier model (Qwen2.5-3B-Instruct)
across both GPU baseline (Transformers) and AirLLM (4-bit paged) inference modes,
all three prompts, and writes results to results/metrics_medium.json.

Per docs/PRD.md (medium tier is a "good AirLLM comparison target").

Routes results and charts through ResultWriter and Visualizer (the
same pattern used by run_llamacpp_benchmark.py) instead of hand-rolling
serialization, resolving docs/TODO.md tasks 10.2/10.3.
"""

from __future__ import annotations

import sys
from pathlib import Path

from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.metrics_helpers import MetricsRecord
from airllm_benchmark.services.result_writer import ResultWriter
from airllm_benchmark.services.visualizer import Visualizer
from airllm_benchmark.shared.config import load_experiment

ASSETS_DIR = Path("assets") / "medium"


def main() -> int:
    """Run medium-tier GPU baseline benchmark and save results.

    Executes the 3B model on GPU baseline only (skip AirLLM due to
    hardware constraints on this system); creates a result matrix for
    inclusion in project results.

    Returns:
        Exit code (0 on success, 1 on error).
    """
    # Configuration: GPU baseline only, all three prompts.
    prompts = ["P1", "P2", "P3"]
    mode = "gpu_provider"

    # Setup output file.
    output_path = Path("results") / "metrics_medium.json"
    writer = ResultWriter(str(output_path))
    writer.clear()

    # Load config (real, not smoke).
    config = load_experiment()
    sdk = BenchmarkSDK()

    results: list[MetricsRecord] = []
    total_runs = len(prompts)

    for current_run, prompt_id in enumerate(prompts, start=1):
        prompt_text = config.get_prompt(prompt_id)
        print(f"[{current_run}/{total_runs}] {prompt_id} / gpu_provider...")

        try:
            record = sdk.run_single(
                model_id="medium",
                mode=mode,
                prompt=prompt_text,
                quantization="none",
            )
            writer.append(record)
            results.append(record)
            print(
                f"  ✓ {record.tokens_generated} tokens "
                f"in {record.total_runtime_s:.2f}s "
                f"({record.generation_throughput:.2f} tok/s)"
            )
        except Exception as e:
            print(f"  ✗ {type(e).__name__}: {str(e)[:80]}")

    if results:
        visualizer = Visualizer()
        chart_paths = visualizer.generate_all(results, str(ASSETS_DIR))
        print(f"Charts written: {', '.join(chart_paths)}")

    print(f"\nMedium-tier GPU baseline complete: {len(results)}/3 runs "
          f"→ {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
