"""Minimal runner pipeline PoC.

End-to-end test that exercises the full runner pipeline:
    RunnerManager → runner → provider → MetricsCollector → MetricsRecord

Verifies every runner mode produces a valid MetricsRecord with all
18 fields correctly populated.

Per docs/TODO.md task 5.6 and docs/IMPLEMENTATION.md PoC rules.

    uv run pytest tests/pocs/test_runner_pipeline_poc.py -v -s
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.sdk.runner import RunnerManager
from airllm_benchmark.services.metrics import MetricsRecord

from .pipeline_helpers import (
    MockProvider,
    assert_record_structure,
    print_record,
)


class TestRunnerPipelinePoC:
    """End-to-end pipeline: RunnerManager → runner → provider → MetricsRecord."""

    @pytest.fixture
    def manager(self) -> RunnerManager:
        """Fresh RunnerManager for each test."""
        return RunnerManager()

    @pytest.fixture
    def provider(self) -> MockProvider:
        """Mock provider implementing InferenceProvider protocol."""
        return MockProvider()

    def test_gpu_provider_pipeline(
        self,
        manager: RunnerManager,
        provider: MockProvider,
    ) -> None:
        """RunnerManager dispatches GPU runner → provider → valid MetricsRecord."""
        runner = manager.get_runner("gpu_provider")
        record = runner.run(
            provider=provider,
            model_id="mock/tiny-model",
            prompt="What is 2+2?",
            max_tokens=16,
            quantization="none",
        )

        assert isinstance(record, MetricsRecord)
        assert_record_structure(record, "gpu_provider")
        print_record(record)

    def test_cpu_baseline_pipeline(
        self,
        manager: RunnerManager,
        provider: MockProvider,
    ) -> None:
        """RunnerManager dispatches CPU runner → provider → valid MetricsRecord."""
        runner = manager.get_runner("cpu_baseline")
        record = runner.run(
            provider=provider,
            model_id="mock/tiny-model",
            prompt="What is 2+2?",
            max_tokens=16,
            quantization="none",
        )

        assert isinstance(record, MetricsRecord)
        assert_record_structure(record, "cpu_baseline")
        print_record(record)

    def test_airllm_pipeline(self, manager: RunnerManager) -> None:
        """RunnerManager dispatches AirLLM runner → builtin → valid MetricsRecord.

        AirLLM is builtin (no provider), so we mock load_model and
        generate_text where they are imported (airllm_runner module).
        Patch where the symbol is looked up, not where it is defined.
        """
        mock_model = MagicMock()
        with (
            patch(
                "airllm_benchmark.sdk.airllm_runner.load_model",
                return_value=mock_model,
            ),
            patch(
                "airllm_benchmark.sdk.airllm_runner.generate_text",
                return_value=("Generated response to: What is 2+2?", 10),
            ),
        ):
            from airllm_benchmark.sdk.airllm_runner import AirllmRunner

            runner = AirllmRunner()
            record = runner.run(
                provider=None,
                model_id="mock/tiny-model",
                prompt="What is 2+2?",
                max_tokens=16,
                quantization="none",
            )

        assert isinstance(record, MetricsRecord)
        assert_record_structure(record, "airllm")
        print_record(record)

    def test_all_modes_dispatch(self, manager: RunnerManager) -> None:
        """RunnerManager correctly dispatches all three modes."""
        modes = manager.get_all_modes()
        assert "gpu_provider" in modes
        assert "cpu_baseline" in modes
        assert "airllm" in modes
        assert len(modes) == 3

    def test_unknown_mode_raises(self, manager: RunnerManager) -> None:
        """RunnerManager rejects unrecognized mode."""
        with pytest.raises(ValueError, match="Unknown inference mode"):
            manager.get_runner("invalid_mode")
