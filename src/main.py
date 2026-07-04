"""CLI entry point for AirLLM Inference Benchmark.

Delegates all business logic to BenchmarkSDK per ADR-001.
Accepts --single for one inference and --run-all for full benchmark.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from airllm_benchmark.cli_printers import (
    print_result,
    print_run_all_result,
    print_validation_result,
)
from airllm_benchmark.sdk.sdk import BenchmarkSDK


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments with mode, model, prompt, and run type.
    """
    parser = argparse.ArgumentParser(
        description="AirLLM Inference Benchmark — Compare GPU, CPU, and AirLLM",
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Run a single inference and print the result.",
    )
    parser.add_argument(
        "--run-all",
        action="store_true",
        help="Run full benchmark across all models, modes, and prompts.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate config, providers, and model cache; run no inference.",
    )
    parser.add_argument(
        "--model",
        default="small",
        help='Model tier (default: "small").',
    )
    parser.add_argument(
        "--mode",
        default="cpu_baseline",
        choices=["gpu_provider", "cpu_baseline", "airllm"],
        help='Inference mode (default: "cpu_baseline").',
    )
    parser.add_argument(
        "--prompt",
        default="What is the capital of France?",
        help="Input prompt text.",
    )
    parser.add_argument(
        "--quantization",
        default="none",
        choices=["none", "4bit", "8bit"],
        help='Quantization level (default: "none").',
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=None,
        help="Optional config directory override.",
    )
    return parser.parse_args(argv)


def run_single(args: argparse.Namespace) -> None:
    """Execute a single inference via SDK and print results.

    Args:
        args: Parsed CLI arguments.
    """
    sdk = BenchmarkSDK(config_dir=args.config_dir)
    record = sdk.run_single(
        model_id=args.model,
        mode=args.mode,
        prompt=args.prompt,
        quantization=args.quantization,
    )
    print_result(record)


def run_all(args: argparse.Namespace) -> None:
    """Execute full benchmark via SDK and print summary.

    Args:
        args: Parsed CLI arguments (only config_dir is used).
    """
    sdk = BenchmarkSDK(config_dir=args.config_dir)
    result = sdk.run_benchmark()
    print_run_all_result(result)


def run_validate(args: argparse.Namespace) -> None:
    """Run pre-benchmark validation via SDK and print the result.

    Per docs/TODO.md task 7.4 — checks config, providers, and model
    cache without executing any inference.

    Args:
        args: Parsed CLI arguments (only config_dir is used).
    """
    sdk = BenchmarkSDK(config_dir=args.config_dir)
    result = sdk.validate()
    print_validation_result(result)


def main(argv: list[str] | None = None) -> None:
    """Entry point: parse args and dispatch to SDK."""
    args = parse_args(argv)

    if args.single:
        run_single(args)
        return

    if args.run_all:
        run_all(args)
        return

    if args.validate:
        run_validate(args)
        return

    # Default: show help when no flag provided
    parse_args(["--help"])


if __name__ == "__main__":
    main()
