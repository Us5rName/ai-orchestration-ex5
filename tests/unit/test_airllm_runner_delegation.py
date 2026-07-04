"""Tests for sdk/airllm_runner.py — Metrics lifecycle and builtin flow.

Verifies AirllmRunner uses MetricsCollector lifecycle correctly
and delegates to load_model + generate_text helpers.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.services.metrics import MetricsRecord


@pytest.fixture
def _mock_collector() -> None:
    """Patch MetricsCollector for all tests in this module."""
    from airllm_benchmark.sdk import airllm_runner

    mock_collector = MagicMock()
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
        tokens_generated=10,
        generation_throughput=10.0,
        peak_ram_mb=100.0,
        peak_vram_mb=0.0,
        status="success",
        error="",
        timestamp="2024-01-01T00:00:00+00:00",
    )
    with patch.object(airllm_runner, "MetricsCollector", return_value=mock_collector):
        yield


class TestAirllmRunnerDelegation:
    """Verify AirllmRunner delegates correctly to helpers."""

    def test_run_delegates_load_model(self, _mock_collector: None) -> None:
        """run() calls load_model() with correct model_id."""
        from airllm_benchmark.sdk.airllm_runner import AirllmRunner

        with patch("airllm_benchmark.sdk.airllm_runner.load_model") as mock_load:
            mock_model = MagicMock()
            mock_load.return_value = mock_model

            with patch("airllm_benchmark.sdk.airllm_runner.generate_text") as mock_gen:
                mock_gen.return_value = ("output text", 5)

                runner = AirllmRunner()
                runner.run(None, "test/model", "Test", 32, "4bit")
                mock_load.assert_called_once_with("test/model", "4bit")

    def test_run_delegates_generate(self, _mock_collector: None) -> None:
        """run() calls generate_text() with prompt and max_tokens."""
        from airllm_benchmark.sdk.airllm_runner import AirllmRunner

        with patch("airllm_benchmark.sdk.airllm_runner.load_model") as mock_load:
            mock_model = MagicMock()
            mock_load.return_value = mock_model

            with patch("airllm_benchmark.sdk.airllm_runner.generate_text") as mock_gen:
                mock_gen.return_value = ("output text", 5)

                runner = AirllmRunner()
                runner.run(None, "test/model", "Hello world", 64, "4bit")
                mock_gen.assert_called_once_with(mock_model, "Hello world", 64)

    def test_run_returns_metrics_record(self, _mock_collector: None) -> None:
        """run() returns a MetricsRecord instance."""
        from airllm_benchmark.sdk.airllm_runner import AirllmRunner

        with patch("airllm_benchmark.sdk.airllm_runner.load_model") as mock_load:
            mock_load.return_value = MagicMock()

            with patch("airllm_benchmark.sdk.airllm_runner.generate_text") as mock_gen:
                mock_gen.return_value = ("output text", 5)

                runner = AirllmRunner()
                result = runner.run(None, "test/model", "Test", 32)
                assert isinstance(result, MetricsRecord)

    def test_run_uses_collector_lifecycle(self, _mock_collector: None) -> None:
        """run() calls collector lifecycle methods in correct order."""
        from airllm_benchmark.sdk import airllm_runner
        from airllm_benchmark.sdk.airllm_runner import AirllmRunner

        with patch("airllm_benchmark.sdk.airllm_runner.load_model") as mock_load:
            mock_load.return_value = MagicMock()

            with patch("airllm_benchmark.sdk.airllm_runner.generate_text") as mock_gen:
                mock_gen.return_value = ("output text", 5)

                runner = AirllmRunner()
                runner.run(None, "test/model", "Test", 32)
                mock_collector = airllm_runner.MetricsCollector.return_value
                calls = [c[0] for c in mock_collector.mock_calls]
                assert "start" in calls
                assert "mark_load_complete" in calls
                assert "stop" in calls
                assert "get_record" in calls

    def test_run_airllm_mode(self, _mock_collector: None) -> None:
        """run() sets mode to airllm in metrics."""
        from airllm_benchmark.sdk import airllm_runner
        from airllm_benchmark.sdk.airllm_runner import AirllmRunner

        with patch("airllm_benchmark.sdk.airllm_runner.load_model") as mock_load:
            mock_load.return_value = MagicMock()

            with patch("airllm_benchmark.sdk.airllm_runner.generate_text") as mock_gen:
                mock_gen.return_value = ("output text", 5)

                runner = AirllmRunner()
                runner.run(None, "test/model", "Test", 32)
                mock_collector = airllm_runner.MetricsCollector.return_value
                start_call = mock_collector.start.call_args
                assert start_call[1]["mode"] == "airllm"

    def test_run_accepts_none_provider(self, _mock_collector: None) -> None:
        """run() accepts None as provider (builtin, no provider)."""
        from airllm_benchmark.sdk.airllm_runner import AirllmRunner

        with patch("airllm_benchmark.sdk.airllm_runner.load_model") as mock_load:
            mock_load.return_value = MagicMock()

            with patch("airllm_benchmark.sdk.airllm_runner.generate_text") as mock_gen:
                mock_gen.return_value = ("output text", 5)

                runner = AirllmRunner()
                result = runner.run(None, "test/model", "Test", 32)
                assert result.status == "success"
