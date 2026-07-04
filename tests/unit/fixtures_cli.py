"""Shared MetricsRecord fixture for CLI tests.

Split out of test_cli.py so both test_cli.py and test_cli_run_all.py
can reuse it without either file crossing the 150-line cap.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_record() -> MagicMock:
    """Deterministic MetricsRecord for CLI assertions."""
    record = MagicMock()
    record.model = "test/small"
    record.mode = "cpu_baseline"
    record.provider = "transformers"
    record.quantization = "none"
    record.prompt = "What is the capital of France?"
    record.status = "success"
    record.load_time_s = 1.0
    record.ttft_s = 1.5
    record.total_runtime_s = 2.5
    record.max_new_tokens = 32
    record.tokens_generated = 10
    record.generation_throughput = 4.0
    record.peak_ram_mb = 100.0
    record.peak_vram_mb = 0.0
    record.error = ""
    record.timestamp = "2026-01-01T00:00:00+00:00"
    return record
