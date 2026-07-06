"""CLI entry point tests — --visualize argument parsing and delegation.

Verifies --visualize argument parsing, ResultWriter.load() +
BenchmarkSDK.generate_visualization() delegation, and output formatting.
All SDK/ResultWriter calls are mocked so tests run without external
dependencies or real chart generation.

Per docs/TODO.md task 10.4 — CLI entry point for generate_visualization().
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.services.visualizer import VisualizationResult
from src.main import parse_args


class TestParseArgsVisualize:
    """CLI --visualize argument parsing tests."""

    def test_visualize_flag(self) -> None:
        """--visualize sets visualize mode."""
        args = parse_args(["--visualize"])
        assert args.visualize is True

    def test_no_flag_defaults_false(self) -> None:
        """No flags leaves visualize as False."""
        args = parse_args([])
        assert args.visualize is False

    def test_default_results_path(self) -> None:
        """--results-path defaults to the canonical results/metrics.json."""
        args = parse_args(["--visualize"])
        assert args.results_path == "results/metrics.json"

    def test_custom_results_path(self) -> None:
        """--results-path overrides the default metrics file."""
        args = parse_args(["--visualize", "--results-path", "results/metrics_medium.json"])
        assert args.results_path == "results/metrics_medium.json"

    def test_default_output_dir(self) -> None:
        """--output-dir defaults to assets."""
        args = parse_args(["--visualize"])
        assert args.output_dir == "assets"


class TestRunVisualize:
    """CLI run_visualize delegation tests."""

    @patch("airllm_benchmark.cli_dispatch.BenchmarkSDK")
    @patch("airllm_benchmark.cli_dispatch.ResultWriter")
    def test_loads_records_and_delegates_to_sdk(self, mock_writer_cls, mock_sdk_cls) -> None:
        """run_visualize loads records via ResultWriter, then calls SDK."""
        from airllm_benchmark.cli_dispatch import run_visualize

        mock_writer = MagicMock()
        mock_writer.load.return_value = ["record-1", "record-2"]
        mock_writer_cls.return_value = mock_writer

        mock_sdk = MagicMock()
        mock_sdk.generate_visualization.return_value = VisualizationResult(
            chart_paths=["assets/latency_chart.png"], table_text="| model | ...|"
        )
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--visualize", "--results-path", "results/metrics_medium.json"])
        run_visualize(args)

        mock_writer_cls.assert_called_once_with("results/metrics_medium.json")
        mock_sdk.generate_visualization.assert_called_once_with(
            ["record-1", "record-2"], output_dir="assets"
        )

    @patch("airllm_benchmark.cli_dispatch.BenchmarkSDK")
    @patch("airllm_benchmark.cli_dispatch.ResultWriter")
    def test_prints_chart_paths_and_table(self, mock_writer_cls, mock_sdk_cls, capsys) -> None:
        """run_visualize prints the chart paths and comparison table."""
        from airllm_benchmark.cli_dispatch import run_visualize

        mock_writer_cls.return_value.load.return_value = []
        mock_sdk = MagicMock()
        mock_sdk.generate_visualization.return_value = VisualizationResult(
            chart_paths=["assets/latency_chart.png", "assets/memory_chart.png"],
            table_text="| model | throughput |",
        )
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--visualize"])
        run_visualize(args)

        output = capsys.readouterr().out
        assert "assets/latency_chart.png" in output
        assert "assets/memory_chart.png" in output
        assert "| model | throughput |" in output

    @patch("airllm_benchmark.cli_dispatch.BenchmarkSDK")
    @patch("airllm_benchmark.cli_dispatch.ResultWriter")
    def test_prints_placeholder_when_no_charts(self, mock_writer_cls, mock_sdk_cls, capsys) -> None:
        """run_visualize prints a placeholder when there are no records."""
        from airllm_benchmark.cli_dispatch import run_visualize

        mock_writer_cls.return_value.load.return_value = []
        mock_sdk = MagicMock()
        mock_sdk.generate_visualization.return_value = VisualizationResult(
            chart_paths=[], table_text="(no records)"
        )
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--visualize"])
        run_visualize(args)

        output = capsys.readouterr().out
        assert "none — no records to visualize" in output
