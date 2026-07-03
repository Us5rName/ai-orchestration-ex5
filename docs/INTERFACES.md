# API Contracts & Interfaces

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.00                                   |
| **Based on**  | `docs/PRD.md` v1.00, `docs/PLAN.md` v1.00 |

---

## 1. SDK Entry Point — `sdk.py`

Single entry point for all benchmark operations. CLI and any external consumer delegate here.

```python
class BenchmarkSDK:
    """Single entry point for all benchmark operations."""

    def run_benchmark(self) -> dict:
        """Execute full benchmark pipeline across all modes.

        Returns:
            dict with keys: summary, chart_paths, table_text
        """

    def run_single(self, model_id: str, mode: str, prompt: str,
                   provider: str | None = None) -> dict:
        """Run a single inference and return metrics.

        Args:
            model_id: HuggingFace model identifier
            mode: one of "gpu_provider", "cpu_baseline", "airllm"
            provider: inference provider (default from config)
            prompt: input text

        Returns:
            dict matching Metrics Record schema (see docs/CONFIG.md)
        """

    def generate_visualization(self) -> list[str]:
        """Generate charts and tables from stored metrics.

        Returns:
            List of file paths to generated assets
        """
```

---

## 2. Provider Interface — `providers/base.py`

All providers in `providers/` implement this protocol. A provider handles model loading and generation for a specific backend (Ollama, Transformers, llama.cpp).

```python
class InferenceProvider(Protocol):
    """Interface for all inference providers."""

    def load_model(self, model_id: str, device: str) -> None:
        """Load model weights onto the target device.

        Args:
            model_id: HuggingFace model identifier or local path
            device: target device ("cuda", "cpu", "mps")
        """

    def generate(self, prompt: str, max_tokens: int) -> str:
        """Generate text from a prompt.

        Args:
            prompt: input text
            max_tokens: maximum tokens to generate

        Returns:
            Generated text
        """

    def unload(self) -> None:
        """Free model weights and associated memory."""
```

### Provider Implementations

| File                        | Provider         | Transport      |
| --------------------------- | ---------------- | -------------- |
| `providers/ollama_provider.py`    | Ollama           | HTTP API       |
| `providers/transformers_provider.py` | Transformers     | Direct (PyTorch) |
| `providers/llamacpp_provider.py`   | llama.cpp        | Python bindings |

---

## 3. Runner Interface — `sdk/runner.py`

Runners orchestrate a single benchmark run. They delegate model loading and generation to a configured `InferenceProvider`.

```python
class InferenceRunner(Protocol):
    """Interface for all inference runners."""

    def run(self, provider: InferenceProvider, model_id: str,
            prompt: str, max_tokens: int) -> dict:
        """Execute one inference run and return metrics.

        Args:
            provider: loaded inference provider
            model_id: HuggingFace model identifier
            prompt: input text
            max_tokens: maximum tokens to generate

        Returns:
            dict matching Metrics Record schema (see docs/CONFIG.md)
        """
```

### Runner Implementations

| File                    | Runner           | Delegates To              |
| ----------------------- | ---------------- | ------------------------- |
| `sdk/gpu_runner.py`     | GPU Runner       | Configured GPU provider   |
| `sdk/cpu_runner.py`     | CPU Baseline Runner | Configured CPU provider |
| `sdk/airllm_runner.py`  | AirLLM Runner    | AirLLM (builtin, no provider) |
