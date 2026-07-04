"""Tests for sdk/cpu_runner.py — Provider delegation and metrics lifecycle.

Verifies CpuRunner delegates load/generate/unload to the provider
and uses MetricsCollector lifecycle correctly.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.services.metrics import MetricsRecord


@pytest.fixture
def mock_provider() -> MagicMock:
    """Create a mock InferenceProvider for CPU tests."""
    provider = MagicMock()
    provider.generate.return_value = ("Generated output text for testing.", 10)
    return provider


@pytest.fixture
def _mock_collector(mock_provider: MagicMock) -> None:
    """Patch MetricsCollector for all tests in this module."""
    from airllm_benchmark.sdk import cpu_runner

    mock_collector = MagicMock()
    mock_collector.get_record.return_value = MetricsRecord(
        run_id="run_1",
        model="test/model",
        mode="cpu_baseline",
        provider="transformers",
        prompt="Test",
        prompt_id="P1",
        quantization="none",
        max_new_tokens=32,
        load_time_s=0.5,
        ttft_s=0.5,
        total_runtime_s=1.0,
        tokens_generated=10,
        generation_throughput=10.0,
        peak_ram_mb=100.0,
        peak_vram_mb=0.0,
        status="success",
        error="",
        timestamp="2024-01-01T00:00:00+00:00",
    )
    with patch.object(cpu_runner, "MetricsCollector", return_value=mock_collector):
        yield


class TestCpuRunnerDelegation:
    """Verify CpuRunner delegates correctly to provider."""

    def test_run_delegates_load_model(
        self, mock_provider: MagicMock, _mock_collector: None
    ) -> None:
        """run() calls provider.load_model() with correct model_id."""
        from airllm_benchmark.sdk.cpu_runner import CpuRunner

        runner = CpuRunner()
        runner.run(mock_provider, "test/model", "Test", 32)
        call_args = mock_provider.load_model.call_args
        assert call_args[0][0] == "test/model"

    def test_run_delegates_load_cpu_device(
        self, mock_provider: MagicMock, _mock_collector: None
    ) -> None:
        """run() calls provider.load_model() with 'cpu' device."""
        from airllm_benchmark.sdk.cpu_runner import CpuRunner

        runner = CpuRunner()
        runner.run(mock_provider, "test/model", "Test", 32)
        call_args = mock_provider.load_model.call_args
        assert call_args[0][1] == "cpu"

    def test_run_delegates_generate(self, mock_provider: MagicMock, _mock_collector: None) -> None:
        """run() calls provider.generate() with prompt and max_tokens."""
        from airllm_benchmark.sdk.cpu_runner import CpuRunner

        runner = CpuRunner()
        runner.run(mock_provider, "test/model", "Hello world", 64)
        mock_provider.generate.assert_called_once_with("Hello world", 64)

    def test_run_delegates_unload(self, mock_provider: MagicMock, _mock_collector: None) -> None:
        """run() calls provider.unload() after generation."""
        from airllm_benchmark.sdk.cpu_runner import CpuRunner

        runner = CpuRunner()
        runner.run(mock_provider, "test/model", "Test", 32)
        mock_provider.unload.assert_called_once()

    def test_run_returns_metrics_record(
        self, mock_provider: MagicMock, _mock_collector: None
    ) -> None:
        """run() returns a MetricsRecord instance."""
        from airllm_benchmark.sdk.cpu_runner import CpuRunner

        runner = CpuRunner()
        result = runner.run(mock_provider, "test/model", "Test", 32)
        assert isinstance(result, MetricsRecord)

    def test_run_uses_collector_lifecycle(
        self, mock_provider: MagicMock, _mock_collector: None
    ) -> None:
        """run() calls collector lifecycle methods in correct order."""
        from airllm_benchmark.sdk import cpu_runner
        from airllm_benchmark.sdk.cpu_runner import CpuRunner

        runner = CpuRunner()
        runner.run(mock_provider, "test/model", "Test", 32)
        mock_collector = cpu_runner.MetricsCollector.return_value
        calls = [c[0] for c in mock_collector.mock_calls]
        assert "start" in calls
        assert "mark_load_complete" in calls
        assert "stop" in calls
        assert "get_record" in calls

    def test_run_cpu_mode(self, mock_provider: MagicMock, _mock_collector: None) -> None:
        """run() sets mode to cpu_baseline in metrics."""
        from airllm_benchmark.sdk import cpu_runner
        from airllm_benchmark.sdk.cpu_runner import CpuRunner

        runner = CpuRunner()
        runner.run(mock_provider, "test/model", "Test", 32)
        mock_collector = cpu_runner.MetricsCollector.return_value
        start_call = mock_collector.start.call_args
        assert start_call[1]["mode"] == "cpu_baseline"
