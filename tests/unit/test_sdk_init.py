"""BenchmarkSDK initialization tests.

Verifies SDK constructor behaviour: config_dir handling, RunnerManager
and Visualizer instantiation.

Per docs/TODO.md task 5.7 — split by interface method.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from airllm_benchmark.sdk.sdk import BenchmarkSDK


class TestSDKInit:
    """BenchmarkSDK initialization tests."""

    def test_default_config_dir(self) -> None:
        """SDK initializes with None config_dir."""
        sdk = BenchmarkSDK()
        assert sdk._config_dir is None

    def test_custom_config_dir(self) -> None:
        """SDK initializes with custom config_dir."""
        sdk = BenchmarkSDK(config_dir="/custom/path")
        assert sdk._config_dir == Path("/custom/path")

    def test_runner_manager_created(self) -> None:
        """SDK creates RunnerManager on init."""
        sdk = BenchmarkSDK()
        assert sdk._runner_mgr is not None

    def test_visualizer_created(self) -> None:
        """SDK creates Visualizer on init."""
        sdk = BenchmarkSDK()
        assert sdk._visualizer is not None


class TestSDKValidate:
    """BenchmarkSDK.validate() delegation tests (docs/TODO.md task 7.4)."""

    def test_delegates_to_run_validation_with_config_dir(self) -> None:
        """validate() forwards the SDK's config_dir to run_validation()."""
        sdk = BenchmarkSDK(config_dir="/custom/path")
        with patch("airllm_benchmark.sdk.sdk.run_validation") as mock_run:
            result = sdk.validate()

        mock_run.assert_called_once_with(Path("/custom/path"))
        assert result is mock_run.return_value
