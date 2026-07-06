"""Shared fixtures/helpers for GPU and AirLLM integration tests.

Split out of ``test_pipeline_gpu.py``/``test_pipeline_airllm.py`` to keep
each test module under the project's 150-raw-line file cap. Per
docs/TODO.md task 10.7.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

SMOKE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
SMOKE_PROMPT = "What is 2+2?"
SMOKE_MAX_TOKENS = 5


def has_cuda() -> bool:
    """Check if CUDA is available on this machine.

    Duplicated (rather than imported from ``tests/pocs/_cuda.py``) so
    ``tests/integration/`` has no dependency on the PoC tier — the two
    suites are documented as independent per docs/TODO.md task 10.7.
    """
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


@pytest.fixture
def gpu_config_dir(tmp_path: Path) -> Path:
    """Write a minimal experiment.json targeting CUDA with tiny token budget.

    Same isolation rationale as ``test_pipeline.py``'s ``sdk_config_dir``:
    keeps this test independent of the real ``config/experiment.json``
    (32 tokens, 32B large tier) so it stays fast regardless of project
    config changes.
    """
    config = {
        "models": {"small": {"id": SMOKE_MODEL, "tier": "small"}},
        "prompts": {"P1": SMOKE_PROMPT},
        "max_new_tokens": SMOKE_MAX_TOKENS,
        "quantization": "none",
        "gpu_provider": "transformers",
        "cpu_baseline_provider": "transformers",
        "provider_config": {"transformers": {"device": "cuda"}},
    }
    config_path = tmp_path / "experiment.json"
    config_path.write_text(json.dumps(config))
    return tmp_path
