# API Contracts & Interfaces

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.02                                   |
| **Based on**  | `docs/PRD.md` v1.00, `docs/PLAN.md` v1.00 |
| **Changes**   | Added §6 Visualizer, §7 VisualizationResult; updated §1 SDK |

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
                   provider: str | None = None) -> MetricsRecord:
        """Run a single inference and return metrics.

        Args:
            model_id: HuggingFace model identifier
            mode: one of "gpu_provider", "cpu_baseline", "airllm"
            provider: inference provider (default from config)
            prompt: input text

        Returns:
            MetricsRecord from this run.
        """

    def generate_visualization(
        self,
        records: list[MetricsRecord],
        output_dir: str = "assets",
    ) -> VisualizationResult:
        """Generate charts and tables from metrics records.

        Args:
            records: List of metrics records to visualize.
            output_dir: Directory to save chart PNGs.

        Returns:
            VisualizationResult with chart_paths and table_text.
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
            prompt: str, max_tokens: int) -> MetricsRecord:
        """Execute one inference run and return metrics.

        Args:
            provider: loaded inference provider
            model_id: HuggingFace model identifier
            prompt: input text
            max_tokens: maximum tokens to generate

        Returns:
            MetricsRecord from this run.
        """
```

### Runner Implementations

| File                    | Runner           | Delegates To              |
| ----------------------- | ---------------- | ------------------------- |
| `sdk/gpu_runner.py`     | GPU Runner       | Configured GPU provider   |
| `sdk/cpu_runner.py`     | CPU Baseline Runner | Configured CPU provider |
| `sdk/airllm_runner.py`  | AirLLM Runner    | AirLLM (builtin, no provider) |

---

## 4. Metrics Record — `services/metrics.py`

Explicit return type for all metrics records. All fields match `docs/CONFIG.md` §1.

```python
@dataclass(frozen=True)
class MetricsRecord:
    """Single metrics record from one inference run."""

    run_id: str
    model: str
    mode: str
    provider: str
    prompt: str
    prompt_id: str
    quantization: str
    max_new_tokens: int
    load_time_s: float
    ttft_s: float
    total_runtime_s: float
    tokens_generated: int
    peak_ram_mb: float
    peak_vram_mb: float
    status: str
    error: str
    timestamp: str
```

---

## 5. Metrics Collector — `services/metrics.py`

The MetricsCollector is used by runners to track timing and memory during inference. Context (model, prompt, etc.) is passed once at `start()`. Only results (tokens, status, error) are passed at `get_record()`.

```python
class MetricsCollector(Protocol):
    """Interface for metrics collection during inference."""

    def start(
        self,
        model_id: str,
        mode: str,
        provider: str,
        prompt: str,
        prompt_id: str,
        quantization: str,
        max_tokens: int,
    ) -> None:
        """Start timing and memory sampling. Store runner context.

        Args:
            model_id: HuggingFace model identifier.
            mode: Inference mode (gpu_provider, cpu_baseline, airllm).
            provider: Provider name (transformers, ollama, llamacpp).
            prompt: Input prompt text.
            prompt_id: Prompt identifier (P1, P2, P3).
            quantization: Quantization level (4bit, 8bit, none).
            max_tokens: Token generation limit.
        """

    def mark_load_complete(self) -> None:
        """Mark model loading as complete. Captures load_time_s."""

    def stop(self) -> None:
        """Stop memory sampling and finalize timing."""

    def get_record(
        self,
        tokens_generated: int,
        status: str,
        error: str = "",
    ) -> MetricsRecord:
        """Assemble metrics record from stored context + internal measurements + results.

        Args:
            tokens_generated: Number of tokens produced.
            status: Run status (success, oom, timeout).
            error: Error message if status != success.

        Returns:
            MetricsRecord matching CONFIG.md §1 schema.
        """
```

---

## 6. Visualization Service — `services/visualizer.py`

Generates charts and comparison tables from metrics records.
All chart output is saved to `assets/` directory as PNG.
Per PRD §3.6 FR-06 and PLAN C3 chart_generator + table_generator.

```python
class Visualizer:
    """Generates charts and tables from inference benchmark metrics."""

    def generate_latency_chart(
        self,
        records: list[MetricsRecord],
        output_dir: str = "assets",
    ) -> str:
        """Generate a bar chart comparing total_runtime_s across modes.

        Args:
            records: List of metrics records to visualize.
            output_dir: Directory to save the chart PNG.

        Returns:
            File path to the generated chart.
        """

    def generate_memory_chart(
        self,
        records: list[MetricsRecord],
        output_dir: str = "assets",
    ) -> str:
        """Generate a bar chart comparing peak_ram_mb across modes.

        Args:
            records: List of metrics records to visualize.
            output_dir: Directory to save the chart PNG.

        Returns:
            File path to the generated chart.
        """

    def generate_table(self, records: list[MetricsRecord]) -> str:
        """Generate a formatted comparison table from metrics records.

        Args:
            records: List of metrics records to tabulate.

        Returns:
            Formatted table string suitable for printing or saving.
        """

    def generate_all(
        self,
        records: list[MetricsRecord],
        output_dir: str = "assets",
    ) -> list[str]:
        """Generate all charts and return their file paths.

        Args:
            records: List of metrics records to visualize.
            output_dir: Directory to save chart PNGs.

        Returns:
            List of file paths to all generated PNG assets.
        """
```

---

## 7. Visualization Result — `services/visualizer.py`

Typed return value for `BenchmarkSDK.generate_visualization()`.

```python
@dataclass(frozen=True)
class VisualizationResult:
    """Result from visualization generation.

    Returned by BenchmarkSDK.generate_visualization().
    """

    chart_paths: list[str]
    table_text: str
```
