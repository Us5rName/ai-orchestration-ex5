"""Extra CLI dispatch functions for AirLLM Inference Benchmark.

Extracted from main.py to respect the 150-line file limit. Holds
the --report and --visualize dispatchers; --single/--run-all/--validate
dispatchers stay in main.py (existing tests patch "src.main.BenchmarkSDK").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from airllm_benchmark.cli_printers import print_report_result, print_visualization_result
from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.result_writer import ResultWriter

if TYPE_CHECKING:
    import argparse

# Canonical default results file per docs/CONFIG.md §1 — the metrics JSON
# path every ResultWriter-based run persists to unless overridden.
DEFAULT_RESULTS_PATH = "results/metrics.json"


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


def add_visualize_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --visualize, --results-path, and --output-dir on the parser.

    Per docs/TODO.md task 10.4 — exposes BenchmarkSDK.generate_visualization()
    (INTERFACES.md §1) from the CLI, previously reachable only via the
    notebook or direct SDK instantiation.
    """
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate charts and a comparison table from persisted metrics.",
    )
    parser.add_argument(
        "--results-path",
        default=DEFAULT_RESULTS_PATH,
        help=f'Metrics JSON file to visualize (default: "{DEFAULT_RESULTS_PATH}").',
    )
    parser.add_argument(
        "--output-dir",
        default="assets",
        help='Directory to save chart PNGs (default: "assets").',
    )


def run_report(args: argparse.Namespace) -> None:
    """Generate the full §5 report via SDK and print the result.

    Args:
        args: Parsed CLI arguments (--report, --assets-dir, config_dir used).
    """
    sdk = BenchmarkSDK(config_dir=args.config_dir)
    result = sdk.generate_report(args.report, output_dir=args.assets_dir)
    print_report_result(result)


def run_visualize(args: argparse.Namespace) -> None:
    """Load persisted metrics and generate charts/table via SDK.

    Args:
        args: Parsed CLI arguments (--results-path, --output-dir,
            config_dir used).
    """
    records = ResultWriter(args.results_path).load()
    sdk = BenchmarkSDK(config_dir=args.config_dir)
    result = sdk.generate_visualization(records, output_dir=args.output_dir)
    print_visualization_result(result)
