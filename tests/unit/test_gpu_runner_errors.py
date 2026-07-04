"""Tests for sdk/gpu_runner.py — Error handling and mode configuration.

Verifies GpuRunner catches OOM and generic errors, cleans up on
failure, and configures metrics with the correct mode.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.services.metrics import MetricsRecord


@pytest.fixture
def mock_provider() -> MagicMock:
    """Create a mock InferenceProvider for GPU error tests."""
    provider = MagicMock()
    provider.generate.return_value = "Generated output text."
    return provider


class TestGpuRunnerErrors:
    """Verify GpuRunner handles errors gracefully."""

    def test_run_catches_oom_error(self, mock_provider: MagicMock) -> None:
        """run() catches OOM errors and returns oom status."""
        from airllm_benchmark.sdk.gpu_runner import GpuRunner

        mock_provider.load_model.side_effect = RuntimeError("CUDA out of memory")

        runner = GpuRunner()
        with patch("airllm_benchmark.sdk.gpu_runner.MetricsCollector") as mock_collector_cls:
            mock_collector = MagicMock()
            mock_collector_cls.return_value = mock_collector
            mock_collector.get_record.return_value = MetricsRecord(
                run_id="run_1",
                model="test/model",
                mode="gpu_provider",
                provider="transformers",
                prompt="Test",
                prompt_id="P1",
                quantization="none",
                max_new_tokens=32,
                load_time_s=0.0,
                ttft_s=0.0,
                total_runtime_s=0.1,
                tokens_generated=0,
                peak_ram_mb=0.0,
                peak_vram_mb=0.0,
                status="oom",
                error="CUDA out of memory",
                timestamp="2024-01-01T00:00:00+00:00",
            )

            result = runner.run(mock_provider, "test/model", "Test", 32)

            assert result.status == "oom"
            assert "out of memory" in result.error.lower()

    def test_run_catches_generic_error(self, mock_provider: MagicMock) -> None:
        """run() catches unexpected errors and returns error status."""
        from airllm_benchmark.sdk.gpu_runner import GpuRunner

        mock_provider.generate.side_effect = Exception("Unexpected failure")

        runner = GpuRunner()
        with patch("airllm_benchmark.sdk.gpu_runner.MetricsCollector") as mock_collector_cls:
            mock_collector = MagicMock()
            mock_collector_cls.return_value = mock_collector
            mock_collector.get_record.return_value = MetricsRecord(
                run_id="run_1",
                model="test/model",
                mode="gpu_provider",
                provider="transformers",
                prompt="Test",
                prompt_id="P1",
                quantization="none",
                max_new_tokens=32,
                load_time_s=0.5,
                ttft_s=0.5,
                total_runtime_s=1.0,
                tokens_generated=0,
                peak_ram_mb=0.0,
                peak_vram_mb=0.0,
                status="error",
                error="Unexpected failure",
                timestamp="2024-01-01T00:00:00+00:00",
            )

            result = runner.run(mock_provider, "test/model", "Test", 32)

            assert result.status == "error"
            assert "Unexpected failure" in result.error

    def test_run_unload_on_error(self, mock_provider: MagicMock) -> None:
        """run() still calls unload() even when an error occurs."""
        from airllm_benchmark.sdk.gpu_runner import GpuRunner

        mock_provider.generate.side_effect = Exception("Test error")

        runner = GpuRunner()
        with patch("airllm_benchmark.sdk.gpu_runner.MetricsCollector") as mock_collector_cls:
            mock_collector = MagicMock()
            mock_collector_cls.return_value = mock_collector

            runner.run(mock_provider, "test/model", "Test", 32)

            mock_provider.unload.assert_called_once()

    def test_run_gpu_mode(self, mock_provider: MagicMock) -> None:
        """run() sets mode to gpu_provider in metrics."""
        from airllm_benchmark.sdk.gpu_runner import GpuRunner

        runner = GpuRunner()
        with patch("airllm_benchmark.sdk.gpu_runner.MetricsCollector") as mock_collector_cls:
            mock_collector = MagicMock()
            mock_collector_cls.return_value = mock_collector
            mock_collector.get_record.return_value = MetricsRecord(
                run_id="run_1",
                model="test/model",
                mode="gpu_provider",
                provider="transformers",
                prompt="Test",
                prompt_id="P1",
                quantization="none",
                max_new_tokens=32,
                load_time_s=0.5,
                ttft_s=0.5,
                total_runtime_s=1.0,
                tokens_generated=10,
                peak_ram_mb=100.0,
                peak_vram_mb=50.0,
                status="success",
                error="",
                timestamp="2024-01-01T00:00:00+00:00",
            )

            runner.run(mock_provider, "test/model", "Test", 32)

            start_call = mock_collector.start.call_args
            assert start_call[1]["mode"] == "gpu_provider"
