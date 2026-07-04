"""Tests for sdk/runner.py — InferenceRunner protocol and RunnerManager.

Verifies protocol compliance and manager dispatch logic.
All external dependencies are mocked per project rules.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from airllm_benchmark.sdk.runner import InferenceRunner, RunnerManager

# ——— Fixtures ———


@pytest.fixture
def mock_runner() -> MagicMock:
    """Create a mock InferenceRunner."""
    runner = MagicMock(spec=InferenceRunner)
    return runner


@pytest.fixture
def mock_metrics_record() -> MagicMock:
    """Create a mock MetricsRecord."""
    record = MagicMock()
    record.status = "success"
    return record


# ——— Protocol Tests ———


class TestInferenceRunnerProtocol:
    """Verify InferenceRunner protocol shape and usage."""

    def test_protocol_requires_run_method(self) -> None:
        """Protocol defines run() method signature."""
        assert hasattr(InferenceRunner, "run")

    def test_mock_satisfies_protocol(self) -> None:
        """A mock with correct spec conforms to InferenceRunner."""
        runner: InferenceRunner = MagicMock(spec=InferenceRunner)
        runner.run.return_value = MagicMock()
        # Should not raise — mock conforms
        assert callable(runner.run)


# ——— RunnerManager Tests ———


class TestRunnerManager:
    """Verify RunnerManager selects the correct runner by mode."""

    def test_get_runner_gpu_provider(self, mock_runner: MagicMock) -> None:
        """gpu_provider mode returns GPU runner."""
        mgr = RunnerManager()
        mgr._gpu_runner = mock_runner
        result = mgr.get_runner("gpu_provider")
        assert result is mock_runner

    def test_get_runner_cpu_baseline(self, mock_runner: MagicMock) -> None:
        """cpu_baseline mode returns CPU runner."""
        mgr = RunnerManager()
        mgr._cpu_runner = mock_runner
        result = mgr.get_runner("cpu_baseline")
        assert result is mock_runner

    def test_get_runner_airllm(self, mock_runner: MagicMock) -> None:
        """airllm mode returns AirLLM runner."""
        mgr = RunnerManager()
        mgr._airllm_runner = mock_runner
        result = mgr.get_runner("airllm")
        assert result is mock_runner

    def test_get_runner_unknown_mode_raises(self) -> None:
        """Unknown mode raises ValueError."""
        mgr = RunnerManager()
        with pytest.raises(ValueError, match="Unknown"):
            mgr.get_runner("invalid_mode")

    def test_get_runner_lazy_initialization(self, mock_runner: MagicMock) -> None:
        """Runners are lazily initialized on first access."""
        from unittest.mock import patch

        mgr = RunnerManager()
        with patch.dict(
            "sys.modules",
            {
                "airllm_benchmark.sdk.gpu_runner": MagicMock(
                    GpuRunner=lambda: mock_runner,
                ),
            },
        ):
            result = mgr.get_runner("gpu_provider")
            assert result is mock_runner

    def test_get_runner_returns_same_instance(self, mock_runner: MagicMock) -> None:
        """Same mode returns cached runner instance."""
        from unittest.mock import patch

        mgr = RunnerManager()
        with patch.dict(
            "sys.modules",
            {
                "airllm_benchmark.sdk.gpu_runner": MagicMock(
                    GpuRunner=lambda: mock_runner,
                ),
            },
        ):
            r1 = mgr.get_runner("gpu_provider")
            r2 = mgr.get_runner("gpu_provider")
            assert r1 is r2

    def test_get_all_modes(self) -> None:
        """get_all_modes returns the three supported modes."""
        mgr = RunnerManager()
        modes = mgr.get_all_modes()
        assert "gpu_provider" in modes
        assert "cpu_baseline" in modes
        assert "airllm" in modes
        assert len(modes) == 3
