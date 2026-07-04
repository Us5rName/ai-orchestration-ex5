"""CLI entry point tests.

Verifies argument parsing, SDK delegation, and output formatting.
All SDK calls are mocked so tests run without external dependencies.

Per docs/TODO.md task 6.1 — POC: CLI → SDK smoke test.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.main import parse_args, run_single


@pytest.fixture
def mock_record() -> MagicMock:
    """Deterministic MetricsRecord for CLI assertions."""
    record = MagicMock()
    record.model = "test/small"
    record.mode = "cpu_baseline"
    record.provider = "transformers"
    record.status = "success"
    record.total_runtime_s = 2.5
    record.tokens_generated = 10
    record.peak_ram_mb = 100.0
    record.error = ""
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
