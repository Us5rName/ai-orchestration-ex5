#!/usr/bin/env python3
"""Parameter sweep for GPU-baseline (small model) inference.

Executes a feasible sweep of prompt × max_new_tokens × quantization
over the GPU baseline (small model tier only) and writes results to
results/metrics_sweep.json.

Per docs/TODO.md task 9.7 (parameter sweep integration).

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

ASSETS_DIR = Path("assets") / "sweep"


def main() -> int:
    """Run parameter sweep and save results.

    Returns:
        Exit code (0 on success, 1 on error).
    """
    # Configuration for the sweep
    # Focus on unquantized baseline; 4bit quantization extremely expensive
    prompts = ["P1", "P2", "P3"]
    max_tokens_list = [8, 32, 128]
    quantizations = ["none"]  # Unquantized only (4bit/8bit too expensive)

    # Setup output file
    output_path = Path("results") / "metrics_sweep.json"
    writer = ResultWriter(str(output_path))
    writer.clear()

    # Load config to resolve prompt text
    config = load_experiment(Path("config") / "smoke")

    # Initialize SDK with smoke config
    sdk = BenchmarkSDK(config_dir=Path("config") / "smoke")

    results: list[MetricsRecord] = []

    # Execute sweep: iterate over all combinations
    total_runs = len(prompts) * len(max_tokens_list) * len(quantizations)
    current_run = 0

    for prompt_id in prompts:
        prompt_text = config.get_prompt(prompt_id)

        for max_tokens in max_tokens_list:
            for quant in quantizations:
                current_run += 1
                print(
                    f"[{current_run}/{total_runs}] {prompt_id} "
                    f"max_new_tokens={max_tokens} quantization={quant}..."
                )

                try:
                    record = sdk.run_single(
                        model_id="small",
                        mode="gpu_provider",
                        prompt=prompt_text,
                        quantization=quant,
                        max_new_tokens=max_tokens,
                    )
                    writer.append(record)
                    results.append(record)
                    print(
                        f"  ✓ {record.tokens_generated} tokens "
                        f"in {record.total_runtime_s:.2f}s "
                        f"({record.generation_throughput:.2f} tok/s)"
                    )
                except Exception as e:
                    print(f"  ✗ Error: {type(e).__name__}: {str(e)[:80]}")
                    print("  Skipping this combination due to error")

    if results:
        visualizer = Visualizer()
        chart_paths = visualizer.generate_all(results, str(ASSETS_DIR))
        print(f"Charts written: {', '.join(chart_paths)}")

    print(f"\nSweep complete: {len(results)} runs written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
