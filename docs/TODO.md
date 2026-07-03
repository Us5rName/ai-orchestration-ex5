# Task Tracking — AirLLM Inference Benchmark

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.00                                   |
| **Based on**  | `docs/PRD.md`, `docs/PLAN.md` v1.00    |
| **Created**   | 2026-07-03                             |

---

## Phase 1 — Project Scaffolding

| #  | Task | Status | Definition of Done |
|----|------|--------|-------------------|
| 1.1 | Create project directory structure (`src/`, `tests/`, `config/`, `results/`, `assets/`, `notebooks/`) | Not Started | All directories exist; matches PLAN C4 code structure |
| 1.2 | Initialize `pyproject.toml` with dependencies (`airllm`, `ollama`, `psutil`, `pytest`, `matplotlib`, `pandas`, `ruff`) | Not Started | `uv sync` succeeds; `uv.lock` generated |
| 1.3 | Create `.env-example` with `HF_TOKEN` placeholder | Not Started | `.env-example` exists; `.env` in `.gitignore` |
| 1.4 | Create `src/airllm_benchmark/__init__.py` with package metadata | Not Started | Package importable; version `1.00` |

---

## Phase 2 — Configuration Layer

| #  | Task | Status | Definition of Done |
|----|------|--------|-------------------|
| 2.1 | Create `config/experiment.json` per [`CONFIG.md`](CONFIG.md) §2 | Not Started | Valid JSON; all required fields present; ruff-clean |
| 2.2 | Create `config/hardware.json` per [`CONFIG.md`](CONFIG.md) §3 | Not Started | Valid JSON; all fields empty (to be filled before benchmarks) |
| 2.3 | Implement `shared/config.py` — loads both JSON files + `.env` | Not Started | Unit tests pass; returns typed config objects; aborts on empty hardware fields |
| 2.4 | Implement `shared/version.py` — version `1.00` | Not Started | Importable; returns correct version string |

---

## Phase 3 — Providers Layer

| #  | Task | Status | Definition of Done |
|----|------|--------|-------------------|
| 3.1 | Create `providers/__init__.py` | Not Started | Exports `InferenceProvider` protocol |
| 3.2 | Implement `providers/base.py` — `InferenceProvider` protocol per [`INTERFACES.md`](INTERFACES.md) §2 | Not Started | Protocol defined; docstrings present |
| 3.3 | Implement `providers/ollama_provider.py` — HTTP client for Ollama API | Not Started | Implements `InferenceProvider`; handles connection errors; unit tests with mocked HTTP |
| 3.4 | Implement `providers/transformers_provider.py` — HuggingFace Transformers wrapper | Not Started | Implements `InferenceProvider`; supports `device` parameter; unit tests with mocked model |
| 3.5 | Implement `providers/llamacpp_provider.py` — llama.cpp Python bindings | Not Started | Implements `InferenceProvider`; unit tests with mocked bindings |

---

## Phase 4 — SDK Layer (Runners)

| #  | Task | Status | Definition of Done |
|----|------|--------|-------------------|
| 4.1 | Implement `sdk/runner.py` — `InferenceRunner` protocol + runner manager per [`INTERFACES.md`](INTERFACES.md) §3 | Not Started | Protocol defined; manager selects runner by mode; unit tests pass |
| 4.2 | Implement `sdk/gpu_runner.py` — delegates to configured GPU provider | Not Started | Loads provider from config; catches OOM; returns metrics dict; unit tests pass |
| 4.3 | Implement `sdk/cpu_runner.py` — delegates to configured CPU provider (no paging) | Not Started | Loads provider from config; catches OOM; returns metrics dict; unit tests pass |
| 4.4 | Implement `sdk/airllm_runner.py` — AirLLM paged inference (builtin, no provider) | Not Started | Loads model via `airllm.AutoModel`; supports 4bit/8bit quantization; returns metrics dict; unit tests pass |
| 4.5 | Implement `sdk/sdk.py` — `BenchmarkSDK` entry point per [`INTERFACES.md`](INTERFACES.md) §1 | Not Started | Orchestrates full pipeline; delegates to runners; unit tests pass |

---

## Phase 5 — Services

| #  | Task | Status | Definition of Done |
|----|------|--------|-------------------|
| 5.1 | Implement `services/metrics.py` — timing + psutil memory sampling | Not Started | Records TTFT, total runtime, peak RAM; 1-second sampling interval; unit tests with mocked psutil |
| 5.2 | Implement `services/visualizer.py` — chart + table generation | Not Started | Generates bar charts (latency, memory), comparison table; saves PNG to `assets/`; unit tests with sample data |

---

## Phase 6 — CLI Entry Point

| #  | Task | Status | Definition of Done |
|----|------|--------|-------------------|
| 6.1 | Implement `src/main.py` — CLI that delegates to `BenchmarkSDK` | Not Started | Accepts `--run-all` and `--single` flags; prints summary; delegates all logic to SDK |

---

## Phase 7 — Tests

| #  | Task | Status | Definition of Done |
|----|------|--------|-------------------|
| 7.1 | `tests/unit/test_config.py` — config loader tests | Not Started | Tests valid JSON, missing fields, empty hardware, env vars; ≥ 85% coverage |
| 7.2 | `tests/unit/test_metrics.py` — metrics collector tests | Not Started | Tests timing accuracy, memory sampling, peak calculation; ≥ 85% coverage |
| 7.3 | `tests/unit/test_providers.py` — provider interface tests | Not Started | Tests protocol compliance; mocked HTTP for Ollama; ≥ 85% coverage |
| 7.4 | `tests/unit/test_visualizer.py` — visualization tests | Not Started | Tests chart generation, table formatting; mocked matplotlib; ≥ 85% coverage |
| 7.5 | `tests/integration/test_pipeline.py` — full pipeline smoke test | Not Started | Runs small model via configured provider; validates metrics output; ≥ 85% coverage |
| 7.6 | Verify global coverage ≥ 85% | Not Started | `uv run pytest --cov` passes; coverage report generated |

---

## Phase 8 — Benchmark Execution

| #  | Task | Status | Definition of Done |
|----|------|--------|-------------------|
| 8.1 | Fill in `config/hardware.json` with actual machine specs | Not Started | All fields populated; no empty values |
| 8.2 | Ollama smoke test — pull small model, verify GPU inference | Not Started | Ollama running; small model generates text; metrics recorded |
| 8.3 | Run GPU baseline — small model via configured provider | Not Started | Metrics in `results/metrics.json`; status = `"success"` |
| 8.4 | Run CPU baseline — large model via configured CPU provider (expect OOM/slowness) | Not Started | Failure or extreme slowness documented; metrics recorded |
| 8.5 | Run AirLLM — same large model via AirLLM (expect success) | Not Started | Model generates text; metrics recorded; status = `"success"` |
| 8.6 | Generate visualizations — charts + comparison table | Not Started | PNGs in `assets/`; table in results summary |

---

## Phase 9 — Analysis & Documentation

| #  | Task | Status | Definition of Done |
|----|------|--------|-------------------|
| 9.1 | Create `notebooks/analysis.ipynb` — Jupyter notebook with results analysis | Not Started | Loads `metrics.json`; generates charts; includes LaTeX formulas; academic references |
| 9.2 | Update `README.md` — installation, usage, configuration, examples | Not Started | Complete per project-setup skill requirements |
| 9.3 | Run `ruff check` — zero violations | Not Started | `uv run ruff check` returns 0 |
| 9.4 | Verify no file exceeds 150 lines | Not Started | All `.py` files ≤ 150 lines |
| 9.5 | Run final checklist per [`final-checklist`](.agents/skills/final-checklist/SKILL.md) | Not Started | All checklist items pass |

---

## Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| 1 — Scaffolding | 4 | 0/4 Done |
| 2 — Configuration | 4 | 0/4 Done |
| 3 — Providers | 5 | 0/5 Done |
| 4 — SDK (Runners) | 5 | 0/5 Done |
| 5 — Services | 2 | 0/2 Done |
| 6 — CLI | 1 | 0/1 Done |
| 7 — Tests | 6 | 0/6 Done |
| 8 — Benchmark Execution | 6 | 0/6 Done |
| 9 — Analysis & Documentation | 5 | 0/5 Done |
| **Total** | **38** | **0/38 Done** |
