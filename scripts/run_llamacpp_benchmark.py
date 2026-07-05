#!/usr/bin/env python3
"""Small-tier llama.cpp GPU-baseline benchmark.

Executes the small-tier model (Qwen2.5-0.5B-Instruct, official GGUF release)
through the llama.cpp provider on the GPU baseline mode, all three prompts,
and writes results to results/metrics_llamacpp.json.

Resolves TODO.md task 10.1: LlamaCppProvider was fully implemented and
unit-tested but never exercised end-to-end or benchmarked against the
Transformers GPU baseline for the same tier. Unlike run_medium_benchmark.py
and run_param_sweep.py, this script routes through ResultWriter and
Visualizer instead of hand-rolling JSON/chart output (see TODO 10.2/10.3).
"""

from __future__ import annotations

import sys
from pathlib import Path

from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.metrics_helpers import MetricsRecord
from airllm_benchmark.services.result_writer import ResultWriter
from airllm_benchmark.services.visualizer import Visualizer
from airllm_benchmark.shared.config import load_experiment

RESULTS_PATH = Path("results") / "metrics_llamacpp.json"
ASSETS_DIR = Path("assets") / "llamacpp"


def main() -> int:
    """Run the llama.cpp small-tier GPU benchmark and save results.

    Returns:
        Exit code (0 on success, 1 on error).
    """
    prompts = ["P1", "P2", "P3"]

    config = load_experiment()
    sdk = BenchmarkSDK()
    writer = ResultWriter(str(RESULTS_PATH))
    writer.clear()

    results: list[MetricsRecord] = []
    total_runs = len(prompts)

    for current_run, prompt_id in enumerate(prompts, start=1):
        prompt_text = config.get_prompt(prompt_id)
        print(f"[{current_run}/{total_runs}] {prompt_id} / llamacpp...")

        try:
            record = sdk.run_single(
                model_id="small_gguf",
                mode="gpu_provider",
                prompt=prompt_text,
                quantization="none",
                provider="llamacpp",
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

    print(
        f"\nllama.cpp small-tier GPU benchmark complete: "
        f"{len(results)}/{total_runs} runs → {RESULTS_PATH}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
