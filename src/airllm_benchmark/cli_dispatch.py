"""Extra CLI dispatch functions for AirLLM Inference Benchmark.

Extracted from main.py to respect the 150-line file limit. Holds
the --report dispatcher; --single/--run-all/--validate dispatchers
stay in main.py (existing tests patch "src.main.BenchmarkSDK").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from airllm_benchmark.cli_printers import print_report_result
from airllm_benchmark.sdk.sdk import BenchmarkSDK

if TYPE_CHECKING:
    import argparse


def add_report_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --report and --assets-dir on the CLI arg parser."""
    parser.add_argument(
        "--report",
        metavar="RESULTS_JSON",
        default=None,
        help="Generate the full §5 report from a persisted metrics JSON file.",
    )
    parser.add_argument(
        "--assets-dir",
        default=None,
        help="Optional override for --report's output directory.",
    )


def run_report(args: argparse.Namespace) -> None:
    """Generate the full §5 report via SDK and print the result.

    Args:
        args: Parsed CLI arguments (--report, --assets-dir, config_dir used).
    """
    sdk = BenchmarkSDK(config_dir=args.config_dir)
    result = sdk.generate_report(args.report, output_dir=args.assets_dir)
    print_report_result(result)
