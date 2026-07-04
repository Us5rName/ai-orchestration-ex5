"""CLI entry point for AirLLM Inference Benchmark.

Delegates all business logic to BenchmarkSDK per ADR-001.
Provides --single flag for running a single inference and printing results.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from airllm_benchmark.sdk.sdk import BenchmarkSDK


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments with mode, model, and prompt.
    """
    parser = argparse.ArgumentParser(
        description="AirLLM Inference Benchmark — Compare GPU, CPU, and AirLLM inference",
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Run a single inference and print the result.",
    )
    parser.add_argument(
        "--model",
        default="small",
        help='Model tier to use (default: "small").',
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
        "--config-dir",
        type=Path,
        default=None,
        help="Optional config directory override.",
    )
    return parser.parse_args(argv)


def run_single(args: argparse.Namespace) -> None:
    """Execute a single inference via the SDK and print results.

    Args:
        args: Parsed CLI arguments.
    """
    sdk = BenchmarkSDK(config_dir=args.config_dir)
    record = sdk.run_single(
        model_id=args.model,
        mode=args.mode,
        prompt=args.prompt,
    )

    print(f"Model:       {record.model}")
    print(f"Mode:        {record.mode}")
    print(f"Provider:    {record.provider}")
    print(f"Status:      {record.status}")
    print(f"Runtime:     {record.total_runtime_s:.2f}s")
    print(f"Tokens:      {record.tokens_generated}")
    print(f"Peak RAM:    {record.peak_ram_mb:.0f} MB")
    if record.error:
        print(f"Error:       {record.error}")


def main(argv: list[str] | None = None) -> None:
    """Entry point: parse args and dispatch to SDK."""
    args = parse_args(argv)

    if args.single:
        run_single(args)
        return

    # Default: show help when no flag provided
    parse_args(["--help"])


if __name__ == "__main__":
    main()
