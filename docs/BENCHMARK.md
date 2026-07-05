# Benchmark Quality Standards

| Metadata      | Value                                    |
| ------------- | ---------------------------------------- |
| **Version**   | 1.00                                     |
| **Based on**  | `docs/PRD.md` v1.00, `docs/PLAN.md` v1.01 |

---

## 1. Purpose

This document defines what is expected from a **good benchmark** within the AirLLM Inference Benchmark project. It establishes quality standards, methodological requirements, and acceptance criteria that distinguish a rigorous, scientifically valid benchmark from a casual performance check.

A good benchmark answers questions reliably — not just once, but consistently, with enough rigor that another researcher can reproduce the results and reach the same conclusions.

---

## 2. Core Principles

### 2.1 Validity

A benchmark must measure what it claims to measure. Each metric must have a clear definition and a direct mapping to the underlying phenomenon:

| Metric | What it measures | Why it matters |
|--------|------------------|----------------|
| `load_time_s` | Model loading + device transfer time | Determines startup cost and cold-start latency |
| `ttft_s` | Time to first token after generation begins | Reflects prompt-processing (prefill) speed |
| `total_runtime_s` | End-to-end inference duration | Captures the full user-perceived latency |
| `generation_throughput` | Tokens generated per second | Measures sustained decoding speed |
| `peak_ram_mb` | Maximum system memory consumed | Determines feasibility on constrained hardware |
| `peak_vram_mb` | Maximum GPU memory consumed | Determines whether the model fits in VRAM |

### 2.2 Reproducibility

A benchmark is only useful if others can verify it. Requirements:

- **Deterministic inputs:** Same model, same prompt, same configuration → same execution path
- **Documented environment:** Hardware specs (`config/hardware.json`), OS, driver versions, Python/runtime versions
- **Pinned dependencies:** All packages pinned via `uv.lock` so the exact runtime environment is reproducible
- **Config-driven:** All tunable parameters externalized to `config/*.json` — no magic numbers in code
- **Seed control:** Random seed recorded per run; generation is deterministic within quantization variance

### 2.3 Fairness

Comparisons must be apples-to-apples:

- **Same model** across all inference modes (GPU, CPU baseline, AirLLM)
- **Same prompt** for each comparison point
- **Same `max_new_tokens`** limit across all runs
- **Same quantization level** where applicable
- **Warm-cold consistency:** Clearly state whether each run is a cold start or warm run; compare equivalent states

### 2.4 Completeness

A good benchmark covers the full decision space relevant to its research question:

- **Model tiers:** Small (fits GPU), Medium (fits GPU, good AirLLM target), Large (exceeds RAM — proves AirLLM value)
- **All three modes:** GPU provider, CPU baseline, AirLLM — each measured under identical conditions
- **Multiple prompts:** Different prompt types (factual, reasoning, code generation) to capture variance
- **Failure scenarios:** Document OOM, timeout, and provider-unavailable cases — these are valid data points

---

## 3. Methodology Requirements

### 3.1 Timing Boundaries

Each metric must measure a well-defined phase — no double-counting, no gaps:

| Metric | Starts At | Ends At | Must Not Include |
|--------|-----------|---------|------------------|
| `load_time_s` | Model loading begins | Model ready for inference | Prompt processing or generation |
| `ttft_s` | Generation starts | First token produced | Model loading or download |
| `total_runtime_s` | First API call | Last token produced | Pre-run setup (config loading, imports) |

A benchmark that conflates download time with load time, or load time with generation time, cannot isolate which phase is the bottleneck.

### 3.2 Model Selection Constraint

The benchmark's purpose is to demonstrate that AirLLM can run models exceeding available memory. This is a **parameter constraint**, not a result requirement:

- **Large model must exceed available RAM unquantized.** If the large model fits in raw CPU memory, the model selection is wrong — the benchmark cannot demonstrate the problem it's designed to study. Choose a larger model or document why the current selection is inappropriate.
- **Failure records must include context.** A bare `oom` status without the model name, memory limits, and error message is uninterpretable.
- **The benchmark reports what happens.** If the model selection is correct and the large model still succeeds on raw CPU (e.g., the hardware changed), that is a valid result. Document it and adjust parameters accordingly.

### 3.3 Warm vs. Cold Separation

Model loading behaves differently on first run (download + load) vs. subsequent runs (load from cache). A good benchmark:

- **Records both states** or clearly documents which state was measured
- **Separates download from transfer** so cached and uncached runs are comparable on the metrics that matter
- **Does not mix states in comparisons** — comparing a cold GPU run against a warm CPU run is meaningless

### 3.4 Statistical Rigor

- **Single-run validity:** For this project scope, a single run per combination is acceptable given the deterministic nature of local inference
- **Variance awareness:** Acknowledge that OS-level background processes, thermal throttling, and GPU power states introduce noise
- **Outlier handling:** If a run's metrics deviate >2 standard deviations from the median of repeated runs, flag it and investigate
- **Confidence notation:** Report results with a caveat about environmental variance; do not claim precision finer than the measurement resolution

---

## 4. Quality Criteria for Benchmark Results

A benchmark run is considered **high-quality** when all of the following hold:

### 4.1 Data Completeness

| Criterion | Requirement |
|-----------|-------------|
| **Coverage** | Every `(model, mode, prompt)` combination produced a record |
| **Field completeness** | All `MetricsRecord` fields populated (non-empty strings, non-null numbers, including `peak_vram_mb`) |
| Status recorded | Every record has a non-empty `status` (`success`, `oom`, or `timeout`) |
| Error context | Every failed record includes a descriptive `error` message |

### 4.2 Metric Reasonableness

| Metric | Sanity Check |
|--------|-------------|
| `load_time_s` | > 0; large model load > small model load |
| `ttft_s` | > 0; GPU mode < CPU mode for same model |
| `total_runtime_s` | > `ttft_s`; scales with token count |
| `generation_throughput` | > 0; GPU mode ≥ CPU mode for same model |
| `peak_ram_mb` | < `hardware.json.ram_gb * 1024` (unless OOM) |
| `peak_vram_mb` | < GPU VRAM capacity (unless OOM) |

### 4.3 Configuration Integrity

| Check | Requirement |
|-------|-------------|
| Hardware documented | All fields in `config/hardware.json` filled |
| Models configured | All three tiers present in `config/experiment.json` |
| Prompts configured | P1, P2, P3 present |
| Providers valid | Configured providers exist and can be instantiated |
| Secrets protected | No API keys in code or committed config files |

---

## 5. Reporting Standards

### 5.1 Summary Table

Every benchmark report must include a comparison table showing:

- Model name and tier
- Inference mode
- Load time, TTFT, total runtime
- Throughput (tokens/sec)
- Peak memory (RAM + VRAM)
- Status (success / oom / timeout)

### 5.2 Visualizations

#### General Requirements

All charts must be:

- **Labeled:** Axis labels with units, title, legend entries
- **Comparable:** Same y-axis scale across charts that compare the same metric
- **Legible:** Minimum 10pt font, sufficient color contrast, 300 DPI PNG output
- **Saved as PNG:** In `assets/` directory with descriptive filenames (e.g., `latency_by_mode.png`)
- **Self-contained:** A viewer should understand the chart without reading surrounding text

#### Required Visualizations

Each visualization below specifies the data, chart type, grouping, and the insight it should convey.

##### V1: Latency Comparison (Grouped Bar Chart)

| Aspect | Specification |
|--------|--------------|
| **Data** | `total_runtime_s` for all run combinations |
| **X-axis** | Model tier (small, medium, large) |
| **Bars per group** | One per mode (gpu_provider, cpu_baseline, airllm), color-coded |
| **Y-axis** | Total runtime (seconds), linear scale |
| **Grouping** | Grouped by model tier; bars within each group represent modes |
| **Insight** | Which mode is fastest per model size; how latency scales with model size |
| **Annotation** | Mark OOM/timeout bars with a hatch pattern or distinct color; add value labels on bars |

##### V2: RAM Usage Comparison (Grouped Bar Chart)

| Aspect | Specification |
|--------|--------------|
| **Data** | `peak_ram_mb` for all successful run combinations |
| **X-axis** | Model tier (small, medium, large) |
| **Bars per group** | One per mode, color-coded |
| **Y-axis** | Peak RAM (MB), linear scale |
| **Grouping** | Grouped by model tier |
| **Insight** | Which mode consumes most system memory; whether AirLLM stays within hardware limits |
| **Annotation** | Add a horizontal reference line at the hardware's total RAM capacity; mark OOM runs explicitly |

##### V2b: VRAM Usage Comparison (Grouped Bar Chart)

| Aspect | Specification |
|--------|--------------|
| **Data** | `peak_vram_mb` for all successful run combinations |
| **X-axis** | Model tier (small, medium, large) |
| **Bars per group** | One per mode, color-coded |
| **Y-axis** | Peak VRAM (MB), linear scale |
| **Grouping** | Grouped by model tier |
| **Insight** | Which mode consumes most GPU memory; whether the model fits in VRAM |
| **Annotation** | Add a horizontal reference line at the GPU's total VRAM capacity; mark OOM runs explicitly |

##### V3: Throughput Comparison (Grouped Bar Chart)

| Aspect | Specification |
|--------|--------------|
| **Data** | `generation_throughput` (tokens/sec) for all successful runs |
| **X-axis** | Model tier |
| **Bars per group** | One per mode, color-coded |
| **Y-axis** | Tokens per second, linear scale |
| **Insight** | Sustained decoding speed per mode; how throughput degrades with model size |

##### V4: Latency Breakdown (Stacked Bar Chart)

| Aspect | Specification |
|--------|--------------|
| **Data** | `load_time_s` + `ttft_s` + (`total_runtime_s` - `ttft_s`) for each run |
| **X-axis** | Model tier × mode (each combination is one bar) |
| **Stack segments** | Load time, TTFT, decoding time (total minus TTFT) |
| **Y-axis** | Seconds, linear scale |
| **Insight** | Which phase dominates latency; whether AirLLM's overhead is in loading or generation |

##### V5: Prompt Sensitivity (Line Chart or Small Multiples)

| Aspect | Specification |
|--------|--------------|
| **Data** | `total_runtime_s` grouped by `prompt_id` (P1, P2, P3) |
| **X-axis** | Prompt ID |
| **Lines/bars** | One per (model, mode) combination, or separate small chart per model tier |
| **Y-axis** | Total runtime (seconds) |
| **Insight** | Whether prompt type/length significantly affects latency; consistency across prompts |

##### V6: Memory vs. Throughput Scatter

| Aspect | Specification |
|--------|--------------|
| **Data** | `peak_ram_mb` (x) vs `generation_throughput` (y) for all successful runs |
| **X-axis** | Peak RAM (MB) |
| **Y-axis** | Throughput (tokens/sec) |
| **Points** | One per run, colored by mode, sized or labeled by model tier |
| **Insight** | Trade-off between memory consumption and throughput; whether AirLLM achieves acceptable throughput at lower memory |

##### V7: VRAM vs. Throughput Scatter

| Aspect | Specification |
|--------|--------------|
| **Data** | `peak_vram_mb` (x) vs `generation_throughput` (y) for all successful runs |
| **X-axis** | Peak VRAM (MB) |
| **Y-axis** | Throughput (tokens/sec) |
| **Points** | One per run, colored by mode, sized or labeled by model tier |
| **Insight** | GPU memory–throughput trade-off; whether GPU-bound modes achieve higher throughput at the cost of VRAM |

#### Recommendations

| **Guideline** | Rationale |
|-----------|----------|
| Use consistent color mapping across all charts (e.g., GPU = blue, CPU = orange, AirLLM = green) | Reduces cognitive load when comparing charts |
| Prefer linear scales over logarithmic unless data spans >2 orders of magnitude | Easier to interpret; log scales hide small but meaningful differences |
| Add data value labels on bars when there are ≤10 bars per chart | Enables precise comparison without eyeballing |
| Sort model tiers by size (small → large) on the x-axis | Natural ordering aids comparison |
| Include a hardware capacity reference line on memory charts (RAM and VRAM) | Contextualizes whether usage is feasible |
| Separate OOM/timeout from successful runs visually | Failure is data, but shouldn't distort scale comparisons |
| Generate charts programmatically from `MetricsRecord` data | Ensures charts always reflect the latest results; no manual editing |
| Save raw data alongside charts (e.g., CSV in `assets/`) | Enables post-hoc analysis or chart regeneration |

### 5.3 Narrative Summary

A good benchmark includes a human-readable summary that:

1. States the hardware environment (CPU, GPU with VRAM capacity, RAM, OS)
2. Summarizes key findings (which mode was fastest, which consumed most RAM and VRAM)
3. Explains the AirLLM trade-off (latency cost vs. feasibility gain)
4. Notes any anomalies or caveats (OOM, zero VRAM, empty prompt_id, etc.)

---

## 6. Anti-Patterns (What a Good Benchmark Avoids)

| Anti-Pattern | Why it's bad | How to avoid |
|--------------|--------------|--------------|
| **Single-point measurement** | One run cannot distinguish signal from noise | Run multiple times or at least acknowledge variance |
| **Comparing different models** | Different architectures have different baseline speeds | Use the same model across all modes |
| **Ignoring cold vs. warm** | Cached models load instantly; uncached models pay download cost | Document warm/cold state; separate download from load time |
| **Silent failures** | Crashed runs leave no record | Catch exceptions; record `oom`/`timeout` status with error message |
| **Hardcoded parameters** | Makes the benchmark non-reproducible on other hardware | Externalize all config to `config/*.json` |
| **Missing hardware context** | Numbers without context are meaningless | Fill `config/hardware.json` before running |
| **Overclaiming precision** | Reporting 12.345678s when measurement noise is ±0.5s | Round to meaningful precision; note measurement resolution |

---

## 7. Validation Checklist

A **run combination** is a unique `(model_tier, mode, prompt_id)` tuple. With 3 tiers × 3 modes × 3 prompts, a full benchmark produces 27 records.

Before declaring a benchmark complete, verify:

- [ ] All 27 run combinations were attempted (3 tiers × 3 modes × 3 prompts)
- [ ] `results/metrics.json` contains a record for every attempted combination
- [ ] Every record has a non-empty `status` (`success`, `oom`, or `timeout`)
- [ ] Every failed record includes a descriptive `error` message
- [ ] Hardware specifications appear in the benchmark output (not just in config)
- [ ] All charts generated and saved in `assets/`
- [ ] Summary table generated
- [ ] `ruff check` returns 0 violations
- [ ] Test coverage ≥ 85%

> **Note:** A benchmark reports what happened — it does not require specific outcomes. If the large model succeeds on raw CPU, that is a valid result that tells you the hardware is sufficient and the benchmark parameters need adjustment. Pre-determining expected results invalidates the benchmark.

---

## 8. Glossary

| Term | Definition |
|------|------------|
| **Cold start** | First run with model not yet loaded into memory |
| **Warm run** | Subsequent run where model is already in memory |
| **TTFT** | Time To First Token — latency from generation start to first output token |
| **Prefill** | Processing the input prompt before generating output tokens |
| **Decoding** | Generating output tokens one at a time |
| **Paged inference** | AirLLM's technique of loading model weights on-demand from disk to memory |
| **Quantization** | Reducing model precision (e.g., FP16 → INT4) to decrease memory footprint |
