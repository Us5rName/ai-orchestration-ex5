"""Tests for shared/config_loader.py — using tests/config/experiment.json.

Validates that the test experiment.json loads correctly
and contains the expected concrete values.
"""

from __future__ import annotations

from pathlib import Path

from airllm_benchmark.shared.config_loader import (
    load_experiment,
)

TEST_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class TestRealExperimentConfig:
    """Tests against the test config/experiment.json file."""

    def test_real_experiment_loads(self) -> None:
        """Test experiment.json exists and loads without error."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg is not None

    def test_real_experiment_small_model(self) -> None:
        """Small model is meta-llama/Llama-3.2-1B."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.get_model_id("small") == "meta-llama/Llama-3.2-1B"

    def test_real_experiment_medium_model(self) -> None:
        """Medium model is Qwen/Qwen2.5-7B-Instruct."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.get_model_id("medium") == "Qwen/Qwen2.5-7B-Instruct"

    def test_real_experiment_large_model(self) -> None:
        """Large model is Qwen/Qwen2.5-72B-Instruct."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.get_model_id("large") == "Qwen/Qwen2.5-72B-Instruct"

    def test_real_experiment_prompt_p1(self) -> None:
        """P1 prompt matches expected text."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.get_prompt("P1") == "What is the capital of the United States?"

    def test_real_experiment_prompt_p2(self) -> None:
        """P2 prompt matches expected text."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.get_prompt("P2") == "Explain quantum entanglement in one paragraph."

    def test_real_experiment_prompt_p3(self) -> None:
        """P3 prompt matches expected text."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.get_prompt("P3") == "Write a Python function that sorts a list."

    def test_real_experiment_max_tokens(self) -> None:
        """max_new_tokens is 32."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.max_new_tokens == 32

    def test_real_experiment_quantization(self) -> None:
        """quantization is 4bit."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.quantization == "4bit"

    def test_real_experiment_gpu_provider(self) -> None:
        """gpu_provider is ollama."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.gpu_provider == "ollama"

    def test_real_experiment_cpu_provider(self) -> None:
        """cpu_baseline_provider is transformers."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.cpu_baseline_provider == "transformers"

    def test_real_experiment_ollama_base_url(self) -> None:
        """Ollama provider config has expected base URL."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.provider_config["ollama"]["base_url"] == "http://localhost:11434"

    def test_real_experiment_transformers_device(self) -> None:
        """Transformers provider config targets cpu."""
        cfg = load_experiment(TEST_CONFIG_DIR)
        assert cfg.provider_config["transformers"]["device"] == "cpu"
