"""Tests for Metrics Record Assembly PoC — assemble_record produces valid metrics dict.

Run:
    uv run pytest tests/pocs/test_metrics_record_poc.py -v
"""

from __future__ import annotations

from pocs.metrics_peak_poc import (
    PeakResult,
    poc_peak_calculation,
)
from pocs.metrics_record_poc import poc_assemble_record
from pocs.metrics_sampling_poc import MemorySample
from pocs.metrics_timing_poc import (
    TimingResult,
    poc_timing,
)


class TestPoCAssembleRecord:
    """Feature PoC: assemble_record produces valid metrics dict."""

    def _get_timing(self) -> TimingResult:
        return poc_timing()

    def _get_peak(self) -> PeakResult:
        return poc_peak_calculation(
            [
                MemorySample(timestamp=0.0, rss_mb=128.5),
            ]
        )

    def test_returns_dict(self) -> None:
        record = poc_assemble_record(
            timing=self._get_timing(),
            peak=self._get_peak(),
            model_id="test/model",
            mode="cpu_baseline",
            prompt="Hello",
            prompt_id="P1",
            max_tokens=32,
            tokens_generated=10,
            status="success",
        )

        assert isinstance(record, dict)

    def test_has_required_keys(self) -> None:
        """Assert record matches CONFIG.md §1 schema."""
        record = poc_assemble_record(
            timing=self._get_timing(),
            peak=self._get_peak(),
            model_id="test/model",
            mode="cpu_baseline",
            prompt="Hello",
            prompt_id="P1",
            max_tokens=32,
            tokens_generated=10,
            status="success",
        )

        required_keys = {
            "run_id",
            "model",
            "mode",
            "provider",
            "prompt",
            "prompt_id",
            "quantization",
            "max_new_tokens",
            "load_time_s",
            "ttft_s",
            "total_runtime_s",
            "tokens_generated",
            "peak_ram_mb",
            "peak_vram_mb",
            "status",
            "error",
            "timestamp",
        }
        assert set(record.keys()) == required_keys

    def test_values_propagated(self) -> None:
        record = poc_assemble_record(
            timing=self._get_timing(),
            peak=self._get_peak(),
            model_id="test/model",
            mode="airllm",
            prompt="Test prompt",
            prompt_id="P2",
            max_tokens=64,
            tokens_generated=20,
            status="success",
        )

        assert record["model"] == "test/model"
        assert record["mode"] == "airllm"
        assert record["prompt_id"] == "P2"
        assert record["max_new_tokens"] == 64
        assert record["tokens_generated"] == 20
        assert record["peak_ram_mb"] == 128.5
