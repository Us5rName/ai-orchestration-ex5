"""Tests for sdk/cpu_runner.py — Error handling and mode configuration.

Verifies CpuRunner catches OOM and generic errors, cleans up on
failure, and classifies MemoryError as OOM status.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.services.metrics import MetricsRecord


@pytest.fixture
def mock_provider() -> MagicMock:
    """Create a mock InferenceProvider for CPU error tests."""
    provider = MagicMock()
    provider.generate.return_value = ("Generated output text.", 10)
    return provider


class TestCpuRunnerErrors:
    """Verify CpuRunner handles errors gracefully."""

    def test_run_catches_oom_error(self, mock_provider: MagicMock) -> None:
        """run() catches MemoryError and returns oom status."""
        from airllm_benchmark.sdk.cpu_runner import CpuRunner

        mock_provider.load_model.side_effect = MemoryError("unable to allocate")

        runner = CpuRunner()
        with patch("airllm_benchmark.sdk.cpu_runner.MetricsCollector") as mock_cls:
            mock_collector = MagicMock()
            mock_cls.return_value = mock_collector
            mock_collector.get_record.return_value = MetricsRecord(
                run_id="run_1",
                model="test/model",
                mode="cpu_baseline",
                provider="transformers",
                prompt="Test",
                prompt_id="P1",
                quantization="none",
                max_new_tokens=32,
                load_time_s=0.0,
                ttft_s=0.0,
                total_runtime_s=0.1,
                tokens_generated=0,
                generation_throughput=0.0,
                peak_ram_mb=0.0,
                peak_vram_mb=0.0,
                status="oom",
                error="unable to allocate",
                timestamp="2024-01-01T00:00:00+00:00",
            )

            result = runner.run(mock_provider, "test/model", "Test", 32)

            assert result.status == "oom"
            assert "unable to allocate" in result.error

    def test_run_catches_generic_error(self, mock_provider: MagicMock) -> None:
        """run() catches unexpected errors and returns error status."""
        from airllm_benchmark.sdk.cpu_runner import CpuRunner

        mock_provider.generate.side_effect = Exception("Unexpected failure")

        runner = CpuRunner()
        with patch("airllm_benchmark.sdk.cpu_runner.MetricsCollector") as mock_cls:
            mock_collector = MagicMock()
            mock_cls.return_value = mock_collector
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
                tokens_generated=0,
                generation_throughput=0.0,
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
        from airllm_benchmark.sdk.cpu_runner import CpuRunner

        mock_provider.generate.side_effect = Exception("Test error")

        runner = CpuRunner()
        with patch("airllm_benchmark.sdk.cpu_runner.MetricsCollector"):
            runner.run(mock_provider, "test/model", "Test", 32)
            mock_provider.unload.assert_called_once()
