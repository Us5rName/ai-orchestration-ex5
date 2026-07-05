# API Contracts & Interfaces

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.07                                   |
| **Based on**  | `docs/PRD.md` v1.00, `docs/PLAN.md` v1.00 |
| **Changes**   | Added `BenchmarkSDK.generate_report()` + `ReportResult` (§1, §11) — additive §5 reporting layer (full table, CSV, six charts, narrative), opt-in via `--report`; Added `BenchmarkSDK.validate()` + `ValidationResult` (§1, §10) per task 7.4; `BenchmarkSummaryResult` (§1) replacing bare dict per INCONSISTENCIES #2. **v1.07**: real TTFT (`MetricsCollector.mark_first_token`, §5); V1 latency chart + legacy `Visualizer` latency chart gained a log-scale y-axis; report layer grew from six to eight charts (added V2b `render_vram_by_tier_chart` and V7 `render_vram_vs_throughput_scatter`, §11); `HardwareConfig` gained `vram_gb`. |

---

## 1. SDK Entry Point — `sdk.py`

Single entry point for all benchmark operations. CLI and any external consumer delegate here.

```python
class BenchmarkSDK:
    """Single entry point for all benchmark operations."""

    def run_benchmark(self) -> BenchmarkSummaryResult:
        """Execute full benchmark pipeline across all modes.

        Returns:
            BenchmarkSummaryResult with summary text, chart paths, and table.
        """

    def run_single(self, model_id: str, mode: str, prompt: str,
                   provider: str | None = None,
                   quantization: str = "none") -> MetricsRecord:
        """Run a single inference and return metrics.

        Args:
            model_id: HuggingFace model identifier
            mode: one of "gpu_provider", "cpu_baseline", "airllm"
            provider: inference provider (default from config)
            prompt: input text
            quantization: quantization level ("4bit", "8bit", "none")

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

    def validate(self) -> ValidationResult:
        """Validate config, providers, and model cache. Runs no inference.

        Per docs/TODO.md task 7.4 — catches misconfiguration (bad config,
        an unconstructible provider) before an expensive benchmark run.
        Model-cache presence is reported but is informational only.

        Returns:
            ValidationResult — see §10.
        """

    def generate_report(
        self, results_path: str, output_dir: str | None = None,
    ) -> ReportResult:
        """Generate the full BENCHMARK.md §5 report from persisted results.

        Additive, opt-in — does not affect run_benchmark()'s existing
        2-chart visualization path. Loads records via ResultWriter.load(),
        then builds the full comparison table, CSV export, eight charts
        (V1-V7 + V2b), and a hardware-aware narrative summary.

        Args:
            results_path: Path to a metrics_<timestamp>.json results file.
            output_dir: Report output directory. Defaults to a per-run
                subdirectory derived from results_path.

        Returns:
            ReportResult — see §11.
        """
```

### 1.1 BenchmarkSummaryResult

Dataclass returned by `BenchmarkSDK.run_benchmark()`.

| Field | Type | Description |
|-------|------|-------------|
| `summary` | str | Human-readable summary text grouped by inference mode |
| `chart_paths` | list[str] | Paths to generated chart PNG files |
| `table_text` | str | Formatted comparison table as a string |

---

## 2. Provider Interface — `providers/base.py`

All providers in `providers/` implement this protocol. A provider handles model loading and generation for a specific backend (Transformers, llama.cpp).

```python
class InferenceProvider(Protocol):
    """Interface for all inference providers."""

    def load_model(self, model_id: str, device: str) -> None:
        """Load model weights onto the target device.

        Args:
            model_id: HuggingFace model identifier or local path
            device: target device ("cuda", "cpu", "mps")
        """

    def generate(self, prompt: str, max_tokens: int) -> tuple[str, int]:
        """Generate text from a prompt.

        Args:
            prompt: input text
            max_tokens: maximum tokens to generate

        Returns:
            Tuple of (generated_text, actual_token_count). Token count is
            the number of tokens in the generated output (excluding prompt).
        """

    def unload(self) -> None:
        """Free model weights and associated memory."""
```

### Provider Implementations

| File                        | Provider         | Transport      |
| --------------------------- | ---------------- | -------------- |
| `providers/transformers_provider.py` | Transformers     | Direct (PyTorch) |
| `providers/llamacpp_provider.py`   | llama.cpp        | Python bindings |

---

## 3. Runner Interface — `sdk/runner.py`

Runners orchestrate a single benchmark run. They delegate model loading and generation to a configured `InferenceProvider`.

```python
class InferenceRunner(Protocol):
    """Interface for all inference runners."""

    def run(self, provider: InferenceProvider, model_id: str,
            prompt: str, max_tokens: int,
            quantization: str = "none") -> MetricsRecord:
        """Execute one inference run and return metrics.

        Args:
            provider: loaded inference provider
            model_id: HuggingFace model identifier
            prompt: input text
            max_tokens: maximum tokens to generate
            quantization: quantization level ("4bit", "8bit", "none")

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
    generation_throughput: float
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
            provider: Provider name (transformers, llamacpp).
            prompt: Input prompt text.
            prompt_id: Prompt identifier (P1, P2, P3).
            quantization: Quantization level (4bit, 8bit, none).
            max_tokens: Token generation limit.
        """

    def mark_download_complete(self) -> None:
        """Mark HF download complete. Separates download from GPU transfer."""

    def mark_load_complete(self) -> None:
        """Mark model loading as complete. Captures load_time_s.

        If mark_download_complete was called, load_time_s = transfer only.
        Otherwise load_time_s = total time since start (includes download).
        """

    def mark_generation_start(self) -> None:
        """Mark generation start. Reference point for TTFT and throughput."""

    def mark_first_token(self) -> None:
        """Mark the moment the first generated token is produced.

        Optional — only called by providers that support a per-token
        callback (currently TransformersProvider, via its optional
        ``_on_first_token`` hook, wired in by GpuRunner/CpuRunner using the
        same duck-typing pattern as ``_on_download_complete``; this is not
        part of the `InferenceProvider` protocol). ``ttft_s`` is
        ``first_token_time - generation_start_time`` when this was called,
        else ``0.0`` (unmeasured for that provider) — never approximated
        from load/setup time.
        """

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

## 7. Result Writer — `services/result_writer.py`

Serializes `MetricsRecord` instances to `results/metrics.json`.
The Runner Manager calls `append(result)` after each run so results
persist incrementally and survive crashes.

```python
class ResultWriter:
    """Persists metrics records to a JSON array file.

    Input:
        output_path (str): File path for metrics.json output.
    Output:
        None (side-effect: writes to file).
    Setup:
        output_path with parent directory existing.
    """

    def __init__(self, output_path: str) -> None:
        """Initialize writer.

        Args:
            output_path: Path to JSON file (e.g. "results/metrics.json").
        """

    def append(self, record: MetricsRecord) -> None:
        """Append a single metrics record to the JSON array file.

        Loads existing records if the file exists, appends the new
        record, and writes back. Creates the file if it does not exist.

        Args:
            record: MetricsRecord to persist.
        """

    def load(self) -> list[MetricsRecord]:
        """Load all persisted records from the JSON array file.

        Returns:
            List of MetricsRecord instances. Empty list if file missing
            or contains no records.
        """

    def clear(self) -> None:
        """Replace the JSON file with an empty array.

        Use before a fresh benchmark run to discard stale data.
        No-ops if the file does not exist.
        """
```

---

## 8. Visualization Result — `services/visualizer.py`

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

---

## 9. API Gatekeeper — `shared/gatekeeper.py`

Rate-limits external calls (HuggingFace Hub downloads) per CLAUDE.md §3.
Every provider/loader that calls an external service wraps the call here
instead of calling it directly. Config comes from `config/rate_limits.json`
(CONFIG.md §5). Overflow calls block until their slot is free — this never
raises due to rate limiting.

```python
def call_with_rate_limit[T](service: str, fn: Callable[[], T]) -> T:
    """Execute fn() through the named service's rate limiter.

    Args:
        service: Rate-limit bucket name (key in config/rate_limits.json).
        fn: Zero-argument callable to execute once the slot is free.

    Returns:
        Whatever fn() returns.

    Raises:
        Exception: Whatever fn() raises — errors are never swallowed.
    """
```

---

## 10. Validation Result — `sdk/sdk_validation.py`

Typed return value for `BenchmarkSDK.validate()`. Per docs/TODO.md task 7.4.

```python
@dataclass(frozen=True)
class ValidationResult:
    """Outcome of a pre-benchmark validation dry-run. No inference is run."""

    config_ok: bool
    config_error: str
    providers: dict[str, bool]
    provider_errors: dict[str, str]
    models_cached: dict[str, bool]

    @property
    def passed(self) -> bool:
        """True if config is valid and every configured provider constructed
        cleanly. Model-cache status is informational only — it does not
        affect this property, since network access can fill the cache.
        """
```

### CLI — `src/main.py`

`--validate` calls `BenchmarkSDK.validate()` and prints the result; it never
runs inference. Exists alongside `--single` and `--run-all`:

| Flag | Delegates to |
| --- | --- |
| `--single` | `BenchmarkSDK.run_single()` |
| `--run-all` | `BenchmarkSDK.run_benchmark()` |
| `--validate` | `BenchmarkSDK.validate()` |
| `--report RESULTS_JSON [--assets-dir DIR]` | `BenchmarkSDK.generate_report()` |
```

---

## 11. Report Builder — `services/report_builder.py`

Additive reporting layer implementing BENCHMARK.md §5: the full 10-column
comparison table, CSV export, eight charts (V1-V7 + V2b, 300 DPI), and a
hardware-aware narrative summary. Pure consumer of `ResultWriter.load()`
output — reads `MetricsRecord` fields, `config/experiment.json` (tier
mapping), and `config/hardware.json` (RAM/VRAM reference lines, hardware
narrative strings). Does not modify `visualizer.py`, `chart_helpers.py`,
`table_helpers.py`, or `sdk_summary.py`; `run_benchmark()`'s existing
2-chart path is unchanged (its latency chart independently gained a
log-scale y-axis — see `services/chart_helpers.py::render_latency_chart`).

```python
@dataclass(frozen=True)
class ReportResult:
    """Full report artifacts. Returned by ReportBuilder.build()."""

    table_text: str
    chart_paths: list[str]
    csv_path: str
    summary_text: str


class ReportBuilder:
    """Builds the full §5 reporting-layer output from metrics records."""

    def build(
        self,
        records: list[MetricsRecord],
        output_dir: str = "assets",
        config_dir: Path | None = None,
    ) -> ReportResult:
        """Build the full report: table, CSV, eight charts, narrative.

        Args:
            records: Metrics records to report on (from ResultWriter.load()).
            output_dir: Directory for CSV + chart PNG output.
            config_dir: Optional config directory override so tier resolution
                uses the same experiment config that produced the metrics.

        Returns:
            ReportResult with all generated artifacts.
        """
```

| Field | Type | Description |
|-------|------|-------------|
| `table_text` | str | Full §5.1 comparison table (Model, Tier, Mode, Load, TTFT, Runtime, Throughput, Peak RAM, Peak VRAM, Status) |
| `chart_paths` | list[str] | Absolute paths to generated V1-V7 (+V2b) chart PNGs (charts with no data are skipped, not included) |
| `csv_path` | str | Absolute path to the exported `metrics.csv` (18 `MetricsRecord` fields + derived `tier`) |
| `summary_text` | str | Hardware-aware narrative: hardware line, key findings, AirLLM trade-off, anomalies |

Chart functions live in `services/report_charts.py` (V1-V3, V2b),
`services/report_charts_extra.py` (V4-V5), and
`services/report_charts_scatter.py` (V6-V7); shared bar-chart rendering is
in `services/report_chart_core.py`; tier/grouping lookups are in
`services/report_helpers.py`; the narrative builder is in
`services/report_narrative.py`.

| Chart | Function | Description |
|-------|----------|--------------|
| V1 | `render_latency_by_tier_chart` | Grouped bar, `total_runtime_s` by tier x mode. Log-scale y-axis (GPU and CPU-raw latency span orders of magnitude). |
| V2 | `render_memory_by_tier_chart` | Grouped bar, `peak_ram_mb` by tier x mode, with a "Total RAM" reference line. |
| V2b | `render_vram_by_tier_chart` | Grouped bar, `peak_vram_mb` by tier x mode, with a "Total VRAM" reference line from `hardware.vram_gb`. |
| V3 | `render_throughput_chart` | Grouped bar, `generation_throughput` by tier x mode (successful runs only). |
| V4 | `render_latency_breakdown_chart` | Stacked bar, Load/TTFT/Generation time by tier x mode. |
| V5 | `render_prompt_sensitivity_chart` | Line chart, `total_runtime_s` by prompt_id, one line per (model, mode). |
| V6 | `render_memory_vs_throughput_scatter` | Scatter, `peak_ram_mb` vs `generation_throughput` (successful runs only). |
| V7 | `render_vram_vs_throughput_scatter` | Scatter, `peak_vram_mb` vs `generation_throughput` (successful runs only). |
