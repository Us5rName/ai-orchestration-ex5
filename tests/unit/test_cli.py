"""CLI entry point tests.

Verifies argument parsing, SDK delegation, and output formatting.
All SDK calls are mocked so tests run without external dependencies.

Per docs/TODO.md task 6.2 — Implement src/main.py CLI.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.main import parse_args, run_all, run_single


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


class TestParseArgs:
    """CLI argument parsing tests."""

    def test_single_flag_default(self) -> None:
        """--single sets single mode with defaults."""
        args = parse_args(["--single"])
        assert args.single is True
        assert args.model == "small"
        assert args.mode == "cpu_baseline"

    def test_custom_model(self) -> None:
        """--model overrides default model tier."""
        args = parse_args(["--single", "--model", "large"])
        assert args.model == "large"

    def test_custom_mode(self) -> None:
        """--mode overrides default inference mode."""
        args = parse_args(["--single", "--mode", "gpu_provider"])
        assert args.mode == "gpu_provider"

    def test_custom_prompt(self) -> None:
        """--prompt overrides default prompt text."""
        args = parse_args(["--single", "--prompt", "Hello world"])
        assert args.prompt == "Hello world"

    def test_invalid_mode_rejected(self) -> None:
        """Invalid --mode raises SystemExit."""
        with pytest.raises(SystemExit):
            parse_args(["--single", "--mode", "invalid"])


class TestRunSingle:
    """CLI run_single delegation tests."""

    @patch("src.main.BenchmarkSDK")
    def test_delegates_to_sdk(self, mock_sdk_cls, mock_record) -> None:
        """run_single calls SDK.run_single with correct args."""
        mock_sdk = MagicMock()
        mock_sdk.run_single.return_value = mock_record
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--single", "--model", "small", "--mode", "cpu_baseline"])
        run_single(args)

        mock_sdk.run_single.assert_called_once_with(
            model_id="small",
            mode="cpu_baseline",
            prompt=args.prompt,
            quantization="none",
        )

    @patch("src.main.BenchmarkSDK")
    def test_prints_result(self, mock_sdk_cls, mock_record, capsys) -> None:
        """run_single prints formatted result."""
        mock_sdk = MagicMock()
        mock_sdk.run_single.return_value = mock_record
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--single"])
        run_single(args)

        output = capsys.readouterr().out
        assert "test/small" in output
        assert "cpu_baseline" in output
        assert "success" in output

    @patch("src.main.BenchmarkSDK")
    def test_prints_error(self, mock_sdk_cls, mock_record, capsys) -> None:
        """run_single prints error message when present."""
        mock_record.error = "OOM: out of memory"
        mock_sdk = MagicMock()
        mock_sdk.run_single.return_value = mock_record
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--single"])
        run_single(args)

        output = capsys.readouterr().out
        assert "OOM: out of memory" in output


class TestParseArgsRunAll:
    """CLI --run-all argument parsing tests."""

    def test_run_all_flag(self) -> None:
        """--run-all sets run_all mode."""
        args = parse_args(["--run-all"])
        assert args.run_all is True
        assert args.single is False

    def test_run_all_and_single_mutual_exclusive(self) -> None:
        """Both --run-all and --single can be set; --single takes precedence."""
        args = parse_args(["--run-all", "--single"])
        assert args.run_all is True
        assert args.single is True

    def test_no_flag_defaults(self) -> None:
        """No flags leaves both run_all and single as False."""
        args = parse_args([])
        assert args.run_all is False
        assert args.single is False


class TestRunAll:
    """CLI run_all delegation tests."""

    @patch("src.main.BenchmarkSDK")
    def test_delegates_to_sdk_run_benchmark(self, mock_sdk_cls) -> None:
        """run_all calls SDK.run_benchmark with correct config_dir."""
        mock_sdk = MagicMock()
        mock_sdk.run_benchmark.return_value = {
            "summary": "Benchmark Summary — 9 runs total",
            "chart_paths": ["assets/latency_chart.png"],
            "table_text": "| Mode | Runtime |",
        }
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--run-all"])
        run_all(args)

        mock_sdk.run_benchmark.assert_called_once()

    @patch("src.main.BenchmarkSDK")
    def test_prints_summary(self, mock_sdk_cls, capsys) -> None:
        """run_all prints formatted benchmark summary."""
        mock_sdk = MagicMock()
        mock_sdk.run_benchmark.return_value = {
            "summary": "Benchmark Summary — 9 runs total",
            "chart_paths": ["assets/latency_chart.png", "assets/memory_chart.png"],
            "table_text": "| Mode | Runtime |\n|------|---------|",
        }
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--run-all"])
        run_all(args)

        output = capsys.readouterr().out
        assert "Benchmark Summary — 9 runs total" in output
        assert "latency_chart.png" in output

    @patch("src.main.BenchmarkSDK")
    def test_prints_table(self, mock_sdk_cls, capsys) -> None:
        """run_all prints comparison table."""
        mock_sdk = MagicMock()
        mock_sdk.run_benchmark.return_value = {
            "summary": "Benchmark Summary",
            "chart_paths": [],
            "table_text": "| gpu_provider | 1.50s |",
        }
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--run-all"])
        run_all(args)

        output = capsys.readouterr().out
        assert "gpu_provider" in output
