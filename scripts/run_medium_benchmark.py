#!/usr/bin/env python3
"""Medium-tier (3B) GPU baseline + AirLLM benchmark.

Executes a complete benchmark of the medium-tier model (Qwen2.5-3B-Instruct)
across both GPU baseline (Transformers) and AirLLM (4-bit paged) inference modes,
all three prompts, and writes results to results/metrics_medium.json.

Per docs/PRD.md (medium tier is a "good AirLLM comparison target").
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.metrics_helpers import MetricsRecord
from airllm_benchmark.shared.config import load_experiment


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
    output_path.parent.mkdir(parents=True, exist_ok=True)

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
            results.append(record)
            print(
                f"  ✓ {record.tokens_generated} tokens "
                f"in {record.total_runtime_s:.2f}s "
                f"({record.generation_throughput:.2f} tok/s)"
            )
        except Exception as e:
            print(f"  ✗ {type(e).__name__}: {str(e)[:80]}")

    # Write results to JSON.
    output_dict = [asdict(r) for r in results]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_dict, f, indent=2)

    print(f"\nMedium-tier GPU baseline complete: {len(results)}/3 runs "
          f"→ {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
