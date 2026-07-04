"""CLI entry point tests — --validate argument parsing and delegation.

Verifies --validate argument parsing and SDK.validate() delegation.
All SDK calls are mocked so tests run without external dependencies.
Split out of test_cli.py to stay within the 150-line cap.

Per docs/TODO.md task 7.4 — POC: config + provider validation.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from airllm_benchmark.sdk.sdk_validation import ValidationResult
from src.main import parse_args, run_validate


class TestParseArgsValidate:
    """CLI --validate argument parsing tests."""

    def test_validate_flag(self) -> None:
        """--validate sets validate mode."""
        args = parse_args(["--validate"])
        assert args.validate is True

    def test_no_flag_defaults_false(self) -> None:
        """No flags leaves validate as False."""
        args = parse_args([])
        assert args.validate is False


class TestRunValidate:
    """CLI run_validate delegation tests."""

    @patch("src.main.BenchmarkSDK")
    def test_delegates_to_sdk_validate(self, mock_sdk_cls) -> None:
        """run_validate calls SDK.validate() exactly once."""
        mock_sdk = MagicMock()
        mock_sdk.validate.return_value = ValidationResult(config_ok=True, config_error="")
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--validate"])
        run_validate(args)

        mock_sdk.validate.assert_called_once()

    @patch("src.main.BenchmarkSDK")
    def test_prints_passed_result(self, mock_sdk_cls, capsys) -> None:
        """run_validate prints PASSED when config and providers are all ok."""
        mock_sdk = MagicMock()
        mock_sdk.validate.return_value = ValidationResult(
            config_ok=True,
            config_error="",
            providers={"transformers": True},
            models_cached={"Qwen/Qwen2.5-0.5B-Instruct": True},
        )
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--validate"])
        run_validate(args)

        output = capsys.readouterr().out
        assert "PASSED" in output
        assert "transformers" in output
        assert "Qwen/Qwen2.5-0.5B-Instruct" in output

    @patch("src.main.BenchmarkSDK")
    def test_prints_config_error(self, mock_sdk_cls, capsys) -> None:
        """run_validate prints the config error and skips provider/cache sections."""
        mock_sdk = MagicMock()
        mock_sdk.validate.return_value = ValidationResult(
            config_ok=False, config_error="Missing required keys: gpu_provider"
        )
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--validate"])
        run_validate(args)

        output = capsys.readouterr().out
        assert "Missing required keys" in output
        assert "Providers" not in output

    @patch("src.main.BenchmarkSDK")
    def test_prints_failed_when_provider_broken(self, mock_sdk_cls, capsys) -> None:
        """run_validate prints FAILED when a provider failed to construct."""
        mock_sdk = MagicMock()
        mock_sdk.validate.return_value = ValidationResult(
            config_ok=True,
            config_error="",
            providers={"ollama": False},
            provider_errors={"ollama": "Unsupported provider: 'ollama'"},
        )
        mock_sdk_cls.return_value = mock_sdk

        args = parse_args(["--validate"])
        run_validate(args)

        output = capsys.readouterr().out
        assert "FAILED" in output
        assert "Unsupported provider" in output
