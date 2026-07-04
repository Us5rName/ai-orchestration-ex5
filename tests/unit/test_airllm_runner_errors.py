"""Tests for sdk/airllm_runner.py — Error handling.

Verifies AirllmRunner catches OOM and generic errors, stops
metrics collection, and returns error status.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.services.metrics import MetricsRecord


class TestAirllmRunnerErrors:
    """Verify AirllmRunner handles errors gracefully."""

    def test_run_catches_oom_error(self) -> None:
        """run() catches MemoryError and returns oom status."""
        from airllm_benchmark.sdk.airllm_runner import AirllmRunner

        with patch("airllm_benchmark.sdk.airllm_runner.load_model") as mock_load:
            mock_load.side_effect = MemoryError("RAM exhausted")

            with patch("airllm_benchmark.sdk.airllm_runner.MetricsCollector") as mock_collector_cls:
                mock_collector = MagicMock()
                mock_collector_cls.return_value = mock_collector
                mock_collector.get_record.return_value = MetricsRecord(
                    run_id="run_1",
                    model="test/model",
                    mode="airllm",
                    provider="airllm",
                    prompt="Test",
                    prompt_id="P1",
                    quantization="4bit",
                    max_new_tokens=32,
                    load_time_s=0.0,
                    ttft_s=0.0,
                    total_runtime_s=0.1,
                    tokens_generated=0,
                    generation_throughput=0.0,
                    peak_ram_mb=0.0,
                    peak_vram_mb=0.0,
                    status="oom",
                    error="RAM exhausted",
                    timestamp="2024-01-01T00:00:00+00:00",
                )

                runner = AirllmRunner()
                result = runner.run(None, "test/model", "Test", 32)

                assert result.status == "oom"

    def test_run_catches_generic_error(self) -> None:
        """run() catches unexpected errors and returns error status."""
        from airllm_benchmark.sdk.airllm_runner import AirllmRunner

        with patch("airllm_benchmark.sdk.airllm_runner.load_model") as mock_load:
            mock_load.side_effect = RuntimeError("Network timeout")

            with patch("airllm_benchmark.sdk.airllm_runner.MetricsCollector") as mock_collector_cls:
                mock_collector = MagicMock()
                mock_collector_cls.return_value = mock_collector
                mock_collector.get_record.return_value = MetricsRecord(
                    run_id="run_1",
                    model="test/model",
                    mode="airllm",
                    provider="airllm",
                    prompt="Test",
                    prompt_id="P1",
                    quantization="4bit",
                    max_new_tokens=32,
                    load_time_s=0.5,
                    ttft_s=0.5,
                    total_runtime_s=1.0,
                    tokens_generated=0,
                    generation_throughput=0.0,
                    peak_ram_mb=0.0,
                    peak_vram_mb=0.0,
                    status="error",
                    error="Network timeout",
                    timestamp="2024-01-01T00:00:00+00:00",
                )

                runner = AirllmRunner()
                result = runner.run(None, "test/model", "Test", 32)

                assert result.status == "error"
                assert "Network timeout" in result.error

    def test_run_stops_collector_on_error(self) -> None:
        """run() calls collector.stop() even when an error occurs."""
        from airllm_benchmark.sdk.airllm_runner import AirllmRunner

        with patch("airllm_benchmark.sdk.airllm_runner.load_model") as mock_load:
            mock_load.side_effect = RuntimeError("Test error")

            with patch("airllm_benchmark.sdk.airllm_runner.MetricsCollector") as mock_collector_cls:
                mock_collector = MagicMock()
                mock_collector_cls.return_value = mock_collector

                runner = AirllmRunner()
                runner.run(None, "test/model", "Test", 32)

                mock_collector.stop.assert_called_once()
