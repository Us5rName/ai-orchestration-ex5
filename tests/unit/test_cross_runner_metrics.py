"""Cross-runner metrics output tests.

Verifies all runners return a valid MetricsRecord with correct
status and token counts on successful inference.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.sdk.airllm_runner import AirllmRunner
from airllm_benchmark.sdk.cpu_runner import CpuRunner
from airllm_benchmark.sdk.gpu_runner import GpuRunner
from airllm_benchmark.services.metrics import MetricsRecord
from tests.unit.fixtures_runner import (
    _make_airllm_record,
    _make_cpu_record,
    _make_gpu_record,
)


@pytest.fixture
def mock_provider() -> MagicMock:
    """Mock InferenceProvider with default success behavior."""
    provider = MagicMock()
    provider.generate.return_value = ("generated output", 15)
    return provider


@pytest.fixture
def _mock_gpu_collector() -> None:
    """Patch MetricsCollector for GPU runner tests."""
    from airllm_benchmark.sdk import gpu_runner

    mock_col = MagicMock()
    mock_col.get_record.return_value = _make_gpu_record()
    with patch.object(gpu_runner, "MetricsCollector", return_value=mock_col):
        yield


@pytest.fixture
def _mock_cpu_collector() -> None:
    """Patch MetricsCollector for CPU runner tests."""
    from airllm_benchmark.sdk import cpu_runner

    mock_col = MagicMock()
    mock_col.get_record.return_value = _make_cpu_record()
    with patch.object(cpu_runner, "MetricsCollector", return_value=mock_col):
        yield


class TestCrossRunnerMetrics:
    """All runners return consistent MetricsRecord on success."""

    def test_gpu_returns_metrics_record(
        self,
        mock_provider: MagicMock,
        _mock_gpu_collector: None,
    ) -> None:
        """GPU runner returns MetricsRecord with success status."""
        result = GpuRunner().run(mock_provider, "m", "p", 32)
        assert isinstance(result, MetricsRecord)
        assert result.status == "success"
        assert result.tokens_generated == 15
        assert result.error == ""

    def test_cpu_returns_metrics_record(
        self,
        mock_provider: MagicMock,
        _mock_cpu_collector: None,
    ) -> None:
        """CPU runner returns MetricsRecord with success status."""
        result = CpuRunner().run(mock_provider, "m", "p", 32)
        assert isinstance(result, MetricsRecord)
        assert result.status == "success"
        assert result.tokens_generated == 15

    def test_airllm_returns_metrics_record(self) -> None:
        """AirLLM runner returns MetricsRecord with success status."""
        runner = AirllmRunner()
        with patch("airllm_benchmark.sdk.airllm_runner.load_model") as ml:
            ml.return_value = MagicMock()
            with patch("airllm_benchmark.sdk.airllm_runner.generate_text") as gt:
                gt.return_value = ("output", 15)
                with patch("airllm_benchmark.sdk.airllm_runner.MetricsCollector") as mc:
                    mock_col = MagicMock()
                    mc.return_value = mock_col
                    mock_col.get_record.return_value = _make_airllm_record()
                    result = runner.run(None, "m", "p", 32, "4bit")
                    assert isinstance(result, MetricsRecord)
                    assert result.status == "success"
