# Product Requirements Document — AirLLM Inference Benchmark

| Metadata      | Value                                           |
| ------------- | ----------------------------------------------- |
| **Version**   | 1.00                                            |
| **Author**    | AI Orchestration Course — Exercise 5            |
| **Created**   | 2026-07-03                                      |
| **Status**    | Draft — Awaiting Approval                       |

---

## 1. Project Overview

### 1.1 Context

Large Language Models (LLMs) demand substantial hardware resources, particularly VRAM on GPUs or RAM on CPUs. Models that exceed available memory either fail to load (OOM — Out Of Memory) or run at impractical speeds due to heavy swapping. **AirLLM** is a runtime library that enables inference of models larger than available memory through **CPU-based paged inference with aggressive quantization** (4-bit / 8-bit). It trades latency for accessibility, allowing models that would otherwise crash to run within constrained environments.

This project demonstrates AirLLM's value proposition by building a reproducible benchmarking pipeline that compares three memory scenarios:

| Scenario                       | Description                                      | Expected Behavior                |
| ------------------------------ | ------------------------------------------------ | -------------------------------- |
| **Small model on GPU**         | Model fits in VRAM; any provider (Ollama, Transformers, etc.) | Fast baseline              |
| **Large model on CPU (raw)**   | Model exceeds available memory; no paging         | OOM or extreme slowness          |
| **Large model via AirLLM**     | Same oversized model; CPU with paged inference    | Succeeds with latency trade-off  |

The key distinction is whether the model fits in available memory — not which provider is used. Providers such as Ollama, Transformers, and llama.cpp can all target GPU or CPU.

### 1.2 Problem Statement

Students and developers with limited GPU memory (or CPU-only machines) cannot run modern LLMs that exceed their hardware capacity. There is no local, reproducible demonstration that quantifies **how much** AirLLM helps — in terms of latency, memory footprint, and throughput — compared to traditional inference methods.

### 1.3 Target Audience

- Course instructors evaluating Exercise 5 submissions
- Peers reviewing benchmarking methodology
- Future students reusing the pipeline for comparative analysis

---

## 2. Goals & Success Metrics

### 2.1 Primary Goals

| #  | Goal                                                        | Priority |
| -- | ----------------------------------------------------------- | -------- |
| G1 | Prove AirLLM can run models that exceed available memory    | **P0**   |
| G2 | Quantify latency, memory, and runtime trade-offs            | **P0**   |
| G3 | Deliver a reproducible, documented benchmarking pipeline    | **P1**   |
| G4 | Produce professional visualizations and analysis            | **P1**   |

### 2.2 Key Performance Indicators (KPIs)

| KPI                              | Target                              | Measurement Method          |
| -------------------------------- | ----------------------------------- | --------------------------- |
| AirLLM loads "too-large" model   | 100% success rate                   | Binary pass/fail            |
| All modes complete inference     | Measured (no predetermined target)  | `time` module               |
| Memory tracking accuracy         | ±5% of actual usage                 | `psutil`                    |
| Test coverage                    | ≥ 85%                               | `pytest-cov`                |
| Ruff violations                  | 0                                   | `ruff check`                |

### 2.3 Acceptance Criteria

- [ ] Ollama is installed and a small model runs successfully (smoke test)
- [ ] A model larger than available memory fails or is excessively slow on raw CPU/GPU (baseline documented)
- [ ] The same model runs successfully via AirLLM
- [ ] Metrics (latency, memory, runtime) are collected for all three modes
- [ ] Results are presented in tables and visualizations
- [ ] All code passes `ruff check` with zero violations
- [ ] No file exceeds 150 lines
- [ ] Test coverage ≥ 85%

---

## 3. Functional Requirements

### 3.1 FR-01: Environment Setup

| Attribute       | Detail                                                        |
| --------------- | ------------------------------------------------------------- |
| **Description** | Provision a `uv`-managed virtual environment with all dependencies |
| **Input**       | `pyproject.toml` with dependency declarations                 |
| **Output**      | Functional `.venv` with Ollama client, AirLLM, psutil, pytest |
| **Constraints** | Must use `uv` exclusively; no `pip` or `venv` commands         |

### 3.2 FR-02: GPU Baseline Smoke Test

| Attribute       | Detail                                                        |
| --------------- | ------------------------------------------------------------- |
| **Description** | Run a small model on GPU via a chosen provider to establish a fast baseline |
| **Input**       | Model identifier, prompt text, provider selection             |
| **Output**      | Generated text, latency (time to first token), runtime        |
| **Constraints** | Model must fit in available VRAM; provider configurable       |

### 3.3 FR-03: Baseline Failure Demonstration

| Attribute       | Detail                                                        |
| --------------- | ------------------------------------------------------------- |
| **Description** | Attempt to load a model too large for available memory without AirLLM |
| **Input**       | Large model identifier (e.g., `Qwen2.5-72B-Instruct`)         |
| **Output**      | OOM error log, or measurement of extreme slowness             |
| **Constraints** | Must document the failure mode (crash vs. swap thrashing)     |

### 3.4 FR-04: AirLLM Inference

| Attribute       | Detail                                                        |
| --------------- | ------------------------------------------------------------- |
| **Description** | Load and generate text using the same large model via AirLLM  |
| **Input**       | Model identifier, prompt, quantization level (4-bit/8-bit)    |
| **Output**      | Generated text, latency, peak RAM usage, total runtime        |
| **Constraints** | Must succeed where FR-03 failed; use CPU inference             |

### 3.5 FR-05: Metrics Collection

| Attribute       | Detail                                                        |
| --------------- | ------------------------------------------------------------- |
| **Description** | Collect and store structured metrics for each inference run   |
| **Input**       | Inference run (any mode)                                      |
| **Output**      | JSON record with fields: `mode`, `model`, `latency_ms`, `peak_ram_mb`, `runtime_s`, `tokens_generated` |
| **Constraints** | Metrics stored in `results/metrics.json`                      |

### 3.6 FR-06: Results Visualization

| Attribute       | Detail                                                        |
| --------------- | ------------------------------------------------------------- |
| **Description** | Generate comparison charts and summary tables                 |
| **Input**       | `results/metrics.json`                                        |
| **Output**      | Bar charts, line graphs, comparison tables in `assets/`       |
| **Constraints** | Charts must be labeled, legible, and saved as PNG             |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| NFR          | Requirement                                                   |
| ------------ | ------------------------------------------------------------- |
| **Latency**  | Measure and report TTFT for each mode; no predetermined target |
| **Memory**   | Record peak RAM usage for each mode                           |
| **Throughput** | Measure tokens/second for each mode                         |

### 4.2 Reliability

| NFR          | Requirement                                                   |
| ------------ | ------------------------------------------------------------- |
| **Reproducibility** | Same seed + same prompt → deterministic token output (within quantization variance) |
| **Error Handling** | Graceful degradation with informative error messages         |

### 4.3 Maintainability

| NFR          | Requirement                                                   |
| ------------ | ------------------------------------------------------------- |
| **Code Quality** | Zero `ruff` violations, ≤150 lines per file, full docstrings |
| **Modularity** | SDK-first architecture; CLI delegates to SDK                  |
| **Configuration** | All tunable values in `config/*.json` or `.env`              |

### 4.4 Security

| NFR          | Requirement                                                   |
| ------------ | ------------------------------------------------------------- |
| **Secrets**  | HuggingFace tokens stored in `.env` only; never in code       |
| **Dependencies** | Pinned versions via `uv.lock`                               |

---

## 5. User Stories

### US-1: Setup and Verification

> **As a** developer,  
> **I want to** install all dependencies with a single `uv` command,  
> **so that** I can quickly reproduce the environment on any machine.

### US-2: GPU Baseline Run

> **As a** researcher,  
> **I want to** run a small model via Ollama and measure its latency,  
> **so that** I have a fast baseline for comparison.

### US-3: Failure Demonstration

> **As a** student,  
> **I want to** attempt loading a model that exceeds my memory,  
> **so that** I can document the failure (OOM or extreme slowness) as baseline.

### US-4: AirLLM Success

> **As a** student,  
> **I want to** run the same oversized model via AirLLM,  
> **so that** I can prove AirLLM enables inference where raw loading fails.

### US-5: Comparative Analysis

> **As a** researcher,  
> **I want to** see a single table/chart comparing GPU vs. CPU vs. AirLLM,  
> **so that** I can articulate the latency-vs-memory trade-off.

---

## 6. Constraints & Dependencies

### 6.1 Benchmarking Hardware

> All metrics are tied to the hardware on which benchmarks run. Results are not portable across different machines. The actual hardware must be documented before running benchmarks.

| Component | Specification |
| --------- | ------------- |
| **CPU**   | *(document actual)* |
| **GPU**   | *(document actual)* |
| **RAM**   | *(document actual)* |
| **Disk**  | *(document actual)* |
| **OS**    | *(document actual)* |

### 6.2 Hardware Constraints

| Resource    | Requirement                                          |
| ----------- | ---------------------------------------------------- |
| **GPU**     | NVIDIA GPU with CUDA support (for Ollama baseline)   |
| **RAM**     | Sufficient system RAM for AirLLM paged inference     |
| **Disk**    | ≥ 20 GB free for model downloads + cache              |

### 6.3 Inference Providers

Multiple providers can perform local inference. The chosen provider is configurable and does not affect the core comparison (model fits vs. model doesn't fit).

| Provider          | GPU Support | CPU Support | Notes                                  |
| ----------------- | ----------- | ----------- | -------------------------------------- |
| **Ollama**        | Yes         | Yes         | Local serving; auto-offloads to GPU    |
| **Transformers**  | Yes         | Yes         | HuggingFace library; direct PyTorch    |
| **llama.cpp**     | Partial     | Yes         | CPU-optimized; GGUF quantization       |
| **GPT4All**       | Yes         | Yes         | Local inference with model library     |

> The benchmark selects a provider via `config/experiment.json`. Ollama is the default for the GPU baseline.

### 6.4 Software Dependencies

| Dependency       | Purpose                          | Version Constraint |
| ---------------- | -------------------------------- | ------------------ |
| `uv`             | Package/environment management   | Latest             |
| `airllm`         | Paged CPU inference              | Latest stable      |
| `ollama`         | GPU inference provider (default) | Latest stable      |
| `psutil`         | Memory/CPU usage monitoring      | ≥ 5.9              |
| `pytest`         | Test framework                   | ≥ 7.0              |
| `matplotlib`     | Visualization                    | ≥ 3.7              |
| `pandas`         | Data manipulation for results    | ≥ 2.0              |

### 6.5 External Services

| Service        | Purpose                    | Authentication     |
| -------------- | -------------------------- | ------------------ |
| **Hugging Face** | Model downloads           | HF Token (`.env`)  |
| **Ollama**     | Local model serving        | None (local)       |

### 6.6 Out of Scope

- Training or fine-tuning models
- Multi-GPU or distributed inference
- Real-time API serving
- Web GUI (CLI-only for this exercise)

---

## 7. Experiment Design

### 7.1 Model Selection Strategy

| Tier          | Model Example                    | Rationale                              |
| ------------- | -------------------------------- | -------------------------------------- |
| **Small**     | `meta-llama/Llama-3.2-1B`        | Fits GPU easily; fast baseline         |
| **Medium**    | `Qwen/Qwen2.5-7B-Instruct`       | Fits GPU; good AirLLM comparison target|
| **Large**     | `Qwen/Qwen2.5-72B-Instruct`      | Exceeds VRAM; demonstrates AirLLM value|

> **Selection Rule:** Choose models based on actual available VRAM. The "Large" model must be **> 2× available VRAM** to guarantee a meaningful failure baseline.

### 7.2 Test Prompts

| Prompt ID | Text                                          | Purpose                    |
| --------- | --------------------------------------------- | -------------------------- |
| P1        | `"What is the capital of the United States?"`  | Simple factual query       |
| P2        | `"Explain quantum entanglement in one paragraph."` | Reasoning/summarization  |
| P3        | `"Write a Python function that sorts a list."`  | Code generation            |

### 7.3 Provider Selection

Both GPU and CPU baseline modes use a configurable provider selected via `config/experiment.json`.

| Mode               | Config Key              | Default        |
| ------------------ | ----------------------- | -------------- |
| GPU baseline       | `gpu_provider`          | `"ollama"`     |
| CPU baseline       | `cpu_baseline_provider` | `"transformers"` |
| AirLLM             | (builtin)               | N/A            |

The same provider can be used for both GPU and CPU modes (e.g., `transformers` with `device: "cuda"` vs `device: "cpu"`).

### 7.4 Metrics Collection Protocol

For each `(model, mode, provider, prompt)` combination:

1. Record **start time** (`time.perf_counter()`)
2. Load model (include load time in metrics)
3. Run inference with `max_new_tokens=32`
4. Record **first-token time** (TTFT — Time To First Token)
5. Record **end time** (total runtime)
6. Sample RAM usage at 1-second intervals via `psutil`
7. Store result in structured JSON

---

## 8. Timeline & Milestones

| Phase | Milestone                              | Estimated Effort | Deliverables                          |
| ----- | -------------------------------------- | ---------------- | ------------------------------------- |
| **1** | Project scaffolding & environment      | 1 hour           | `pyproject.toml`, `uv.lock`, `.env`   |
| **2** | Ollama smoke test                      | 1 hour           | GPU baseline run, metrics             |
| **3** | Baseline failure demonstration         | 1 hour           | OOM log or slow-run metrics           |
| **4** | AirLLM inference implementation        | 2 hours          | SDK module, successful run            |
| **5** | Metrics collection & storage           | 1 hour           | `results/metrics.json`                |
| **6** | Visualization & analysis notebook      | 2 hours          | Charts in `assets/`, Jupyter notebook |
| **7** | Tests, linting, documentation          | 2 hours          | ≥85% coverage, zero ruff violations   |
| **8** | Final review & submission              | 1 hour           | Complete PRD, PLAN, TODO, README      |

**Total Estimated Effort:** ~10 hours

---

## 9. Risk Assessment

| Risk                              | Likelihood | Impact | Mitigation                                    |
| --------------------------------- | ---------- | ------ | --------------------------------------------- |
| GPU unavailable / broken          | Medium     | High   | Use CPU-only baseline; document limitation    |
| AirLLM compatibility issues       | Low        | High   | Test with small model first; fallback to 8-bit|
| Model download fails (network)    | Medium     | Medium | Pre-download models; cache locally            |
| HF token required for gated model | High       | Medium | Use open models (Qwen, Llama-3.2) by default  |
| Insufficient system RAM           | Low        | High   | Reduce model size; use 4-bit quantization     |

---

## 10. Glossary

| Term              | Definition                                                            |
| ----------------- | --------------------------------------------------------------------- |
| **AirLLM**        | Library for running LLMs larger than available memory via CPU paging  |
| **TTFT**          | Time To First Token — latency until the first generated token         |
| **OOM**           | Out Of Memory — error when hardware cannot allocate required memory   |
| **Quantization**  | Reducing model precision (e.g., 16-bit → 4-bit) to save memory       |
| **Paged Inference** | Loading model weights on-demand from disk, similar to OS virtual memory |
| **Ollama**        | Local LLM serving tool; supports both GPU and CPU inference           |
| **Inference Provider** | Software that executes model inference (Ollama, Transformers, llama.cpp, etc.) |
