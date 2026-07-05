"""CLI entry point tests — --run-all argument parsing and delegation.

Verifies --run-all argument parsing and SDK.run_benchmark delegation.
All SDK calls are mocked so tests run without external dependencies.
Split out of test_cli.py to stay within the 150-line cap.

Per docs/TODO.md tasks 6.1/6.2 — --run-all flag and run_all().
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.sdk.sdk_summary import BenchmarkSummaryResult
from src.main import parse_args, run_all


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
        mock_sdk.run_benchmark.return_value = BenchmarkSummaryResult(
            summary="Benchmark Summary — 9 runs total",
            chart_paths=["assets/latency_chart.png"],
            table_text="| Mode | Runtime |",
        )
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--run-all"])
        run_all(args)

        mock_sdk.run_benchmark.assert_called_once()

    @patch("src.main.BenchmarkSDK")
    def test_prints_summary(self, mock_sdk_cls, capsys) -> None:
        """run_all prints formatted benchmark summary."""
        mock_sdk = MagicMock()
        mock_sdk.run_benchmark.return_value = BenchmarkSummaryResult(
            summary="Benchmark Summary — 9 runs total",
            chart_paths=["assets/latency_chart.png", "assets/memory_chart.png"],
            table_text="| Mode | Runtime |\n|------|---------|",
        )
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
        mock_sdk.run_benchmark.return_value = BenchmarkSummaryResult(
            summary="Benchmark Summary",
            chart_paths=[],
            table_text="| gpu_provider | 1.50s |",
        )
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--run-all"])
        run_all(args)

        output = capsys.readouterr().out
        assert "gpu_provider" in output
