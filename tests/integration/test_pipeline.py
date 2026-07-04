"""Full pipeline integration smoke test.

Exercises ``BenchmarkSDK.run_single()`` end-to-end against a real, small
HuggingFace model (``Qwen/Qwen2.5-0.5B-Instruct``) via ``TransformersProvider``
on CPU. Unlike ``tests/pocs/test_runner_pipeline_poc.py`` (which uses a
``MockProvider``), this is a genuine integration test: it downloads (or
reuses the HF cache for) real model weights and performs real inference,
so it belongs in ``tests/integration/`` rather than ``tests/unit/``.

Follows the same "real model, real runner" pattern as
``tests/pocs/test_cpu_runner_benchmark_poc.py`` — same open model (no HF
auth needed) — but drives it through the full SDK entry point instead of
constructing the runner directly, per docs/TODO.md task 9.6.

    uv run pytest tests/integration/test_pipeline.py -v -s
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.metrics import MetricsRecord

# Small, open model — no HF auth needed. Matches config/experiment.json's
# "small" tier and tests/pocs/test_cpu_runner_benchmark_poc.py's POC_MODEL.
SMOKE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
SMOKE_PROMPT = "What is 2+2?"
SMOKE_MAX_TOKENS = 5


@pytest.fixture
def sdk_config_dir(tmp_path: Path) -> Path:
    """Write a minimal experiment.json with a tiny ``max_new_tokens``.

    Isolated from the real ``config/experiment.json`` (which drives the
    Phase 8 benchmark matrix with 32 tokens per prompt) so this smoke
    test stays fast — well under a minute — regardless of the project's
    real experiment settings.
    """
    config = {
        "models": {"small": {"id": SMOKE_MODEL, "tier": "small"}},
        "prompts": {"P1": SMOKE_PROMPT},
        "max_new_tokens": SMOKE_MAX_TOKENS,
        "quantization": "none",
        "gpu_provider": "transformers",
        "cpu_baseline_provider": "transformers",
        # Explicit "cpu" so this test never touches a CUDA driver, even
        # though CpuRunner already forces CPU via its DEFAULT_DEVICE.
        "provider_config": {"transformers": {"device": "cpu"}},
    }
    config_path = tmp_path / "experiment.json"
    config_path.write_text(json.dumps(config))
    return tmp_path


def _assert_smoke_record(record: MetricsRecord) -> None:
    """Assert MetricsRecord fields for a successful CPU pipeline run.

    Mirrors the assertion style of
    ``tests/pocs/test_cpu_runner_benchmark_poc.py``'s ``_assert_common``.
    """
    assert record.status == "success", f"Run failed: {record.error}"
    assert record.model == SMOKE_MODEL
    assert record.mode == "cpu_baseline"
    assert record.provider == "transformers"
    assert record.prompt == SMOKE_PROMPT
    assert record.quantization == "none"
    assert record.max_new_tokens == SMOKE_MAX_TOKENS
    assert record.run_id.startswith("run_"), "Run ID should be prefixed"
    assert record.timestamp, "Timestamp should be set"
    assert record.error == "", "Error should be empty on success"

    assert record.load_time_s > 0, "Load time should be positive"
    assert record.ttft_s > 0, "TTFT should be positive"
    assert record.total_runtime_s > 0, "Total runtime should be positive"
    assert record.ttft_s >= record.load_time_s, "TTFT >= load_time"
    assert record.total_runtime_s >= record.ttft_s, "Runtime >= TTFT"

    assert record.tokens_generated > 0, "Should have generated tokens"
    assert record.generation_throughput > 0, "Throughput must be positive"

    assert record.peak_ram_mb > 0, "RAM usage should be measurable"


def test_full_pipeline_cpu_smoke(sdk_config_dir: Path) -> None:
    """BenchmarkSDK.run_single() runs a real small model end-to-end on CPU.

    Exercises the full pipeline — SDK -> config loading -> provider
    creation -> CpuRunner -> TransformersProvider -> MetricsCollector —
    producing a real ``MetricsRecord`` from a real (tiny) HF model, using
    the same public entry point the CLI (``src/main.py``) delegates to.
    """
    sdk = BenchmarkSDK(config_dir=sdk_config_dir)

    record = sdk.run_single(
        model_id="small",
        mode="cpu_baseline",
        prompt=SMOKE_PROMPT,
        provider="transformers",
        quantization="none",
    )

    assert isinstance(record, MetricsRecord)
    _assert_smoke_record(record)
