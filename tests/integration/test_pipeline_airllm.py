"""Full pipeline integration test — AirLLM runner on real CUDA hardware.

Extends the CPU coverage in ``test_pipeline.py`` per docs/TODO.md task
10.7: ``tests/integration/`` previously had no test exercising the
AirLLM runner end-to-end — that coverage only existed in
``tests/pocs/`` (``test_airllm_metrics_poc.py``,
``test_airllm_runner_poc.py``), which is documented as proof-of-concept
work, not the integration suite.

Drives the same public entry point as ``test_full_pipeline_cpu_smoke``
— ``BenchmarkSDK.run_single()`` — with the small 0.5B model directly
rather than the default 32B ``large`` scenario (docs/PROMPT_LOG.md
Entry 58: the full 32B AirLLM run takes ~18 minutes, disproportionate
for a test suite).

    uv run pytest tests/integration/test_pipeline_airllm.py -v -s
"""

from __future__ import annotations

from pathlib import Path

import pytest

from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.metrics import MetricsRecord

from ._gpu_common import SMOKE_MAX_TOKENS, SMOKE_MODEL, SMOKE_PROMPT, gpu_config_dir, has_cuda

__all__ = ["gpu_config_dir"]


@pytest.mark.skipif(not has_cuda(), reason="CUDA not available — integration test requires GPU hardware")
def test_full_pipeline_airllm_smoke(gpu_config_dir: Path) -> None:
    """BenchmarkSDK.run_single() runs AirLLM paged inference end-to-end.

    Uses the small 0.5B model directly (not the 32B ``large`` tier) so
    this stays fast — AirLLM's paged loading works correctly at any
    model size, and the small model is enough to prove the runner path
    end-to-end without a ~18 minute run.
    """
    sdk = BenchmarkSDK(config_dir=gpu_config_dir)

    record = sdk.run_single(
        model_id=SMOKE_MODEL,
        mode="airllm",
        prompt=SMOKE_PROMPT,
        quantization="4bit",
        max_new_tokens=SMOKE_MAX_TOKENS,
    )

    assert isinstance(record, MetricsRecord)
    assert record.status == "success", f"Run failed: {record.error}"
    assert record.model == SMOKE_MODEL
    assert record.mode == "airllm"
    assert record.provider == "airllm"
    assert record.prompt == SMOKE_PROMPT
    assert record.quantization == "4bit"
    assert record.max_new_tokens == SMOKE_MAX_TOKENS
    assert record.error == "", "Error should be empty on success"

    assert record.load_time_s > 0, "Load time should be positive"
    # AirllmRunner never wires a per-token callback into MetricsCollector
    # (only TransformersProvider does, via `_on_first_token` — see
    # MetricsCollector.mark_first_token's docstring in services/metrics.py).
    # So ttft_s is documented to fall back to 0.0 for this runner; this is
    # by-design unmeasured latency, not the known CPU-smoke-test flake.
    assert record.ttft_s == 0.0, "AirLLM does not measure per-token TTFT (documented fallback)"
    assert record.total_runtime_s > 0, "Total runtime should be positive"
    assert record.tokens_generated > 0, "Should have generated tokens"
    assert record.generation_throughput > 0, "Throughput must be positive"
    assert record.peak_ram_mb > 0, "RAM usage should be measurable"

    print("\n===== AirLLM Integration Smoke =====")
    print(
        f"load_time_s={record.load_time_s:.3f} ttft_s={record.ttft_s:.3f} "
        f"total_runtime_s={record.total_runtime_s:.3f} tokens={record.tokens_generated} "
        f"throughput={record.generation_throughput:.2f} peak_ram_mb={record.peak_ram_mb:.1f} "
        f"peak_vram_mb={record.peak_vram_mb:.1f}"
    )
    print("=====================================\n")
