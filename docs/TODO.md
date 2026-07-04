# Task Tracking — AirLLM Inference Benchmark

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.00                                   |
| **Based on**  | `docs/PRD.md`, `docs/PLAN.md` v1.00    |
| **Created**   | 2026-07-03                             |

> **TDD Rule:** Tests are written alongside each phase, not after. Each task that produces code includes its tests. Global coverage gate at the end.
> **Dependencies:** `Depends` column lists tasks that must complete first.
> **Integration:** Staged bottom-up. Each phase integrates with the previous before moving on. See [Integration Plan](#integration-plan).

---

## Phase 1 — Project Scaffolding

| #  | Task | Status | Definition of Done |
|----|------|--------|-------------------|
| 1.1 | Create project directory structure (`src/`, `tests/`, `config/`, `results/`, `assets/`, `notebooks/`) | ✅ Done | All directories exist; matches PLAN C4 code structure |
| 1.2 | Initialize `pyproject.toml` with dependencies (`airllm`, `ollama`, `psutil`, `pytest`, `matplotlib`, `pandas`, `ruff`) | ✅ Done | `uv sync` succeeds; `uv.lock` generated |
| 1.3 | Create `.env-example` with `HF_TOKEN` placeholder | ✅ Done | `.env-example` exists; `.env` in `.gitignore` |
| 1.4 | Create `src/airllm_benchmark/__init__.py` with package metadata | ✅ Done | Package importable; version `1.00` |

---

## Phase 2 — Configuration Layer

| #  | Task | Depends | Status | Definition of Done |
|----|------|---------|--------|-------------------|
| 2.1 | Create `config/experiment.json` per [`CONFIG.md`](CONFIG.md) §2 | 1.1 | ✅ Done | Valid JSON; all required fields present |
| 2.2 | Create `config/hardware.json` per [`CONFIG.md`](CONFIG.md) §3 | 1.1 | ✅ Done | Valid JSON; all fields empty (filled in Phase 8) |
| 2.3 | Implement `shared/config.py` — loads both JSON files + `.env` | 2.1, 2.2 | ✅ Done | Returns typed config objects; aborts on empty hardware fields |
| 2.4 | `tests/unit/test_config.py` — config loader tests | 2.3 | ✅ Done | 15 tests: valid JSON, missing fields, empty hardware, env vars |
| 2.5 | Implement `shared/version.py` — version `1.00` | 1.4 | ✅ Done | Importable; returns correct version string (done Phase 1) |

---

## Phase 3 — Providers Layer

| #  | Task | Depends | Status | Definition of Done |
|----|------|---------|--------|-------------------|
| 3.1 | Create `providers/__init__.py` | 1.1 | ✅ Done | Exports `InferenceProvider` protocol |
| 3.2 | Implement `providers/base.py` — `InferenceProvider` protocol per [`INTERFACES.md`](INTERFACES.md) §2 | 3.1 | ✅ Done | Protocol defined; docstrings present |
| 3.3 | Implement `providers/ollama_provider.py` — HTTP client for Ollama API | 3.2 | ~~Not Started~~ | **Removed** — transformers used as GPU provider instead |
| 3.4 | Implement `providers/transformers_provider.py` — HuggingFace Transformers wrapper | 3.2 | ✅ Done | Implements `InferenceProvider`; supports `device` parameter (CPU and GPU) |
| 3.4.1 | Verify GPU execution with real CUDA test | 3.4 | ✅ Done | RTX 4080 SUPER test: tiny model loads on cuda:0, generates text, unloads |
| 3.4.2 | Verify CPU execution with real test | 3.4 | ✅ Done | CPU test: tiny model loads, generates text, unloads |
| ⚠️ | | | | **Caution:** Transformers imports PyTorch. Test with mocked model to avoid downloading weights during unit tests. |
| 3.5 | Implement `providers/llamacpp_provider.py` — llama.cpp Python bindings | 3.2 | ✅ Done | Implements `InferenceProvider`; wraps `llama_cpp.Llama` (thin provider + `llamacpp_helpers.py` split for model-source resolution/loading, matching the transformers pattern); supports local `.gguf` paths and `"repo_id::filename"` HF-Hub identifiers via `from_pretrained()`; `device` mapped to `n_gpu_layers` (`0` = CPU, `-1` = full GPU offload); HF-Hub fetch routed through `call_with_rate_limit("huggingface", ...)`; `uv sync` built `llama-cpp-python` cleanly, no toolchain blockers hit |
| ⚠️ | | | | **Caution:** Each provider wraps a different runtime (HTTP, PyTorch, native bindings). Test isolation is critical — mock all external calls. |
| 3.6 | `tests/unit/test_providers.py` — provider interface tests | 3.3, 3.4, 3.5 | ✅ Done | Tests protocol compliance; all external calls mocked (split into `test_providers.py` + `test_provider_lifecycle.py` + `test_llamacpp_load.py`/`test_llamacpp_generate.py`/`test_llamacpp_unload.py`/`test_llamacpp_lifecycle.py`, 36 llama.cpp tests, 100% coverage on both llamacpp files) |
| 3.7 | Implement `shared/gatekeeper.py` + `config/rate_limits.json` — rate-limited external calls per `CLAUDE.md` §3 | 2.3 | ✅ Done | `call_with_rate_limit()` wraps HF Hub calls in `transformers_helpers.py` and `airllm_loader.py`; never raises on overflow |
| 3.8 | `tests/unit/test_gatekeeper.py` — gatekeeper tests | 3.7 | ✅ Done | Tests RateLimiter timing (mocked clock), config loading, exception propagation; 9 tests pass |

---

## Phase 4 — Services

> Moved before SDK so runners can depend on metrics collection.

| #  | Task | Depends | Status | Definition of Done |
|----|------|---------|--------|-------------------|
| 4.1 | Implement `services/metrics.py` — timing + psutil memory sampling | 1.1 | Done | Records TTFT, total runtime, peak RAM; 1-second sampling interval |
| 4.2 | `tests/unit/test_metrics.py` — metrics collector tests | 4.1 | ✅ Done | Tests timing accuracy, memory sampling, peak calculation; mocked psutil (split into `test_metrics_collector.py`, `test_metrics_sampler.py`, `test_metrics_edge_cases.py`) |
| 4.3 | POC: minimal metrics + visualization pipeline | 4.1 | ✅ Done | End-to-end test: collect fake metrics → generate chart → verify PNG output (15 tests, `pocs/visualization_pipeline_poc.py`) |
| 4.4 | Implement `services/visualizer.py` — chart + table generation | 4.3 | ✅ Done | Generates bar charts (latency, memory), comparison table; saves PNG to `assets/` (split: `visualizer.py` + `chart_helpers.py` + `table_helpers.py`, 19 tests) |
| 4.5 | `tests/unit/test_visualizer.py` — visualization tests | 4.4 | ✅ Done | Tests chart generation, table formatting; split into `test_visualizer_charts.py`, `test_visualizer_table.py`, `test_visualizer_generate_all.py` (19 tests, all pass) |

---

## Phase 5 — SDK Layer (Runners)

| #  | Task | Depends | Status | Definition of Done |
|----|------|---------|--------|-------------------|
| 5.1 | Implement `sdk/runner.py` — `InferenceRunner` protocol + runner manager per [`INTERFACES.md`](INTERFACES.md) §3 | 3.2, 2.3 | ✅ Done | Protocol defined; manager selects runner by mode; 9 tests pass |
| 5.2 | Implement `sdk/gpu_runner.py` — delegates to configured GPU provider | 5.1, 4.1 | ✅ Done | Delegates to provider; catches OOM; returns MetricsRecord; 11 tests pass |
| ⚠️ | | | | **Caution:** GPU runner depends on provider availability. OOM can occur if model exceeds VRAM. Mock provider in tests. |
| 5.3 | Implement `sdk/cpu_runner.py` — delegates to configured CPU provider (no paging) | 5.1, 4.1 | ✅ Done | Loads provider from config; catches OOM (MemoryError); returns MetricsRecord; 12 tests pass |
| ⚠️ | | | | **Caution:** CPU runner may OOM or hang on large models. Set timeout. Mock provider in tests. |
| 5.4 | Implement `sdk/airllm_runner.py` — model loading + quantization | 4.1 | ✅ Done | Loads model via `airllm.AutoModel`; supports 4bit/8bit quantization; 11 tests pass |
| ⚠️ | | | | **Caution:** AirLLM uses paged inference with on-demand weight loading. Split across helper functions to stay under 150 lines. Mock AirLLM in tests. |
| 5.5 | Implement `sdk/airllm_runner.py` — generation + metrics collection | 5.4 | ✅ Done | Generates text via `generate_text()`; collects metrics via `MetricsCollector`; returns MetricsRecord; 11 unit tests + 3 PoCs pass |
| 5.6 | POC: minimal runner pipeline | 5.2, 5.3, 5.5 | ✅ Done | End-to-end test: runner manager → provider → metrics → verify output dict structure; 5 tests pass |
| 5.7 | Implement `sdk/sdk.py` — `BenchmarkSDK` entry point per [`INTERFACES.md`](INTERFACES.md) §1 | 5.1, 5.2, 5.3, 5.5, 4.4, ResultWriter | ✅ Done | Orchestrates full pipeline; delegates to runners; persists via ResultWriter; 4 test files (12 tests) + 3 PoCs pass |
| 5.8 | `tests/unit/test_runners.py` — cross-runner tests | 5.2, 5.3, 5.5 | ✅ Done | Tests runner dispatch, OOM handling, metrics output, param propagation; 14 tests + 8 PoCs pass |

---

## Phase 6 — CLI Entry Point

| #  | Task | Depends | Status | Definition of Done |
|----|------|---------|--------|-------------------|
| 6.1 | POC: CLI → SDK smoke test | 5.7 | ✅ Done | CLI accepts `--single`, delegates to SDK.run_single(), prints MetricsRecord — 8 tests pass |
| 6.2 | Implement `src/main.py` — CLI that delegates to `BenchmarkSDK` | 6.1 | ✅ Done | Accepts `--run-all` and `--single` flags; prints summary; delegates all logic to SDK — 14 tests pass, ruff=0, real validation done |

---

## Integration Plan

Integration follows a **staged bottom-up** approach. Each phase integrates with the previous before advancing. No phase moves forward with broken contracts.

### Integration Strategy

| Stage | What Integrates | Verification | Rollback |
|-------|----------------|--------------|----------|
| **I1** | Config → Providers | Provider loads config, validates provider_config section | Fix config schema; re-run test_config |
| **I2** | Providers → Metrics | Provider generates text; metrics collector records timing + RAM | Mock provider; verify metrics isolation |
| **I3** | Metrics → Runners | Runner delegates to provider + metrics; returns metrics dict | Mock both; verify runner output structure |
| **I4** | Runners → SDK | SDK dispatches to runners; aggregates results | Mock runners; verify SDK aggregation |
| **I5** | SDK → CLI | CLI calls SDK; prints summary | Mock SDK; verify CLI delegation |
| **I6** | Full pipeline (mocked) | End-to-end with all mocks; validates data flow | Isolate failing contract; fix before real run |
| **I7** | Real config + real provider (Ollama) + small model | Config loads real JSON; Ollama provider connects; small model generates text | Verify Ollama running; check base_url |
| **I8** | Real config + real provider (Transformers) + small model | Transformers provider loads small model on CPU; generates text | Verify transformers import; no GPU required |
| **I9** | Real provider + real metrics (Ollama) | Same as I7 but metrics collector samples real process memory | Verify psutil readings match system monitor |
| **I10** | Real GPU runner (Ollama + real metrics) | GPU runner executes small model via Ollama; returns real metrics dict | Verify metrics dict matches schema; status = success |
| **I11** | Real CPU runner (Transformers + real metrics) | CPU runner executes small model via Transformers; returns real metrics dict | Verify no OOM on small model; metrics recorded |
| **I12** | Real AirLLM runner (AirLLM + real metrics) | AirLLM runner executes small model; returns real metrics dict | Verify AirLLM loads; metrics recorded |
| **I13** | Real SDK + real runners (all three modes, small model) | SDK orchestrates all three runners; aggregates results | Verify all three modes produce valid metrics |
| **I14** | Real CLI + real SDK (small model) | CLI calls SDK; prints summary | Verify CLI output matches expected format |
| **I15** | Full benchmark (large model, all modes) | Phase 8 benchmark execution with large model | Reduce model size; increase quantization; swap provider |

### Contract Verification

Each integration stage verifies the data contract between modules:

| Contract | Producer | Consumer | Verification |
|----------|----------|----------|-------------|
| Config object | `shared/config.py` | All modules | Typed dict; all fields present |
| Provider output | `providers/*.py` | Runners | String text; no exceptions on valid input |
| Metrics dict | `services/metrics.py` | Runners, Visualizer | Matches [`CONFIG.md`](CONFIG.md) §1 schema |
| Runner result | `sdk/*_runner.py` | SDK | Metrics dict with `status` field |
| SDK summary | `sdk/sdk.py` | CLI | Dict with `summary`, `chart_paths`, `table_text` |

### Mock vs Real Progression

| Stage | Providers | Models | Metrics | External Services |
|-------|-----------|--------|---------|-------------------|
| Unit tests | Mocked | Mocked | Mocked psutil | None |
| POC steps | Mocked | Mocked | Real (fake data) | None |
| I1–I6 | Mocked | Mocked | Real | None |
| I7 | Real (Ollama) | Small (real) | Mocked | Ollama |
| I8 | Real (Transformers) | Small (real) | Mocked | HF Hub |
| I9 | Real (Ollama) | Small (real) | Real | Ollama |
| I10 | Real (Ollama) | Small (real) | Real | Ollama |
| I11 | Real (Transformers) | Small (real) | Real | HF Hub |
| I12 | Real (AirLLM) | Small (real) | Real | HF Hub |
| I13 | All real | Small (real) | Real | All providers |
| I14 | All real | Small (real) | Real | All providers |
| I15 | All real | Large (real) | Real | All providers |

### Integration Checkpoints

Each checkpoint must pass before advancing to the next phase:

| Checkpoint | Gate | Command |
|------------|------|--------|
| **CP1** (after Phase 2) | Config loads without errors | `uv run pytest tests/unit/test_config.py` |
| **CP2** (after Phase 3) | All providers pass protocol compliance | `uv run pytest tests/unit/test_providers.py` |
| **CP3** (after Phase 4) | Metrics + visualizer produce output from fake data | `uv run pytest tests/unit/test_metrics.py tests/unit/test_visualizer.py` |
| **CP4** (after Phase 5) | All runners return valid metrics dict (mocked) | `uv run pytest tests/unit/test_runners.py` |
| **CP5** (after Phase 6) | CLI delegates to SDK; prints result (mocked) | `uv run python src/main.py --single --mock` |
| **CP6** (after I6) | Full mocked pipeline passes | `uv run pytest tests/integration/test_pipeline.py --mock` |
| **CP7** (after I7) | Real Ollama provider returns text for small model | `uv run python src/main.py --single --provider ollama --model small` |
| **CP8** (after I8) | Real Transformers provider returns text for small model | `uv run python src/main.py --single --provider transformers --model small` |
| **CP9** (after I10) | GPU runner (Ollama) returns valid metrics for small model | `uv run python src/main.py --single --mode gpu --model small` |
| **CP10** (after I11) | CPU runner (Transformers) returns valid metrics for small model | `uv run python src/main.py --single --mode cpu --model small` |
| **CP11** (after I12) | AirLLM runner returns valid metrics for small model | `uv run python src/main.py --single --mode airllm --model small` |
| **CP12** (after I13) | All three modes succeed on small model | `uv run python src/main.py --run-all --model small` |
| **CP12** (after Phase 7) | Validation dry-run passes; no inference | `uv run python src/main.py --validate` |

### Failure Protocol

When an integration checkpoint fails:

1. **Isolate** — identify which contract is broken (producer or consumer)
2. **Revert** — last known passing commit; do not accumulate broken changes
3. **Fix** — repair the contract; re-run only the failing checkpoint
4. **Verify** — re-run all previous checkpoints to ensure no regression
5. **Advance** — only when all checkpoints pass

---

## Phase 7 — Pre-Benchmark Preparation

| #  | Task | Depends | Status | Definition of Done |
|----|------|---------|--------|-------------------|
| 7.1 | Handle gated model access — accept HuggingFace terms for Llama models | 1.3 | Not Started | Model accessible via HF API; token in `.env` |
| ⚠️ | | | | **Caution:** Gated models (Llama) require manual term acceptance on HuggingFace before any API access works. |
| 7.2 | Pre-download all models to HF cache | 7.1 | Not Started | All three model tiers cached locally; no network needed during benchmarks |
| ⚠️ | | | | **Caution:** 72B model download is large (~140 GB unquantized). Verify disk space before starting. |
| 7.3 | Fill in `config/hardware.json` with actual machine specs | 2.2 | ✅ Done | All fields populated; no empty values |
| 7.4 | POC: config + provider validation | 2.3, 3.3, 3.4, 7.2, 7.3 | Not Started | SDK validates config is consistent, provider is reachable, models are cached — no inference executed |
| ⚠️ | | | | **Caution:** This step catches misconfiguration before expensive benchmark runs. Do not skip. |

---

## Phase 8 — Benchmark Execution

| #  | Task | Depends | Status | Definition of Done |
|----|------|---------|--------|-------------------|
| 8.1 | Ollama smoke test — pull small model, verify GPU inference | 7.4 | Not Started | Ollama running; small model generates text; metrics recorded |
| 8.2 | Run GPU baseline — small model via configured provider | 8.1 | Not Started | Metrics in `results/metrics.json`; status = `"success"` |
| 8.3 | Run CPU baseline — large model via configured CPU provider | 8.2 | Not Started | Failure (OOM) or extreme slowness documented; metrics recorded |
| ⚠️ | | | | **Caution:** This run may crash or hang. Set a timeout. If it hangs, kill the process and record the timeout as the result. |
| 8.4 | Run AirLLM — same large model via AirLLM | 8.3 | Not Started | Model generates text; metrics recorded; status = `"success"` |
| ⚠️ | | | | **Caution:** AirLLM with 72B model on CPU will be slow. Monitor RAM usage. If system becomes unresponsive, reduce model size or increase quantization. |
| 8.5 | POC: full benchmark pipeline | 8.4 | Not Started | End-to-end: GPU baseline → CPU baseline → AirLLM → metrics stored → visualizations generated |
| 8.6 | Generate visualizations — charts + comparison table | 8.5 | Not Started | PNGs in `assets/`; table in results summary |

---

## Phase 9 — Analysis & Documentation

| #  | Task | Depends | Status | Definition of Done |
|----|------|---------|--------|-------------------|
| 9.1 | Create `notebooks/analysis.ipynb` — Jupyter notebook with results analysis | 8.6 | Not Started | Loads `metrics.json`; generates charts; includes LaTeX formulas; academic references |
| 9.2 | Verify global test coverage ≥ 85% | 2.4, 3.6, 4.2, 4.5, 5.8 | ✅ Done | `uv run pytest --cov` passes (89.6%); coverage report generated; gated in CI |
| 9.3 | Run `ruff check` — zero violations | 6.2 | ✅ Done | `uv run ruff check` returns 0 (`src tests scripts`); gated in CI |
| 9.4 | Verify no file exceeds 150 lines | 6.2 | ✅ Done | All `.py` files ≤ 150 lines; gated in CI via `scripts/check_line_cap.py` |
| 9.5 | Update `README.md` — installation, usage, configuration, examples | 8.6 | ✅ Done | Adopted hw5-bundle starter README with generated repo-facts region |
| 9.6 | `tests/integration/test_pipeline.py` — full pipeline smoke test | 5.7 | Not Started | Runs small model via configured provider; validates metrics output |
| 9.7 | Run final checklist per [`final-checklist`](.agents/skills/final-checklist/SKILL.md) | 9.2, 9.3, 9.4, 9.5 | Not Started | All checklist items pass |

---

## Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| 1 — Scaffolding | 4 | 4/4 Done |
| 2 — Configuration | 5 | 5/5 Done |
| 3 — Providers | 9 | 9/9 Done (3.3 ollama removed, excluded from count) |
| 4 — Services | 5 | 5/5 Done |
| 5 — SDK (Runners) | 8 | 8/8 Done |
| 6 — CLI | 2 | 2/2 Done |
| 7 — Pre-Benchmark | 4 | 1/4 Done |
| 8 — Benchmark Execution | 6 | 0/6 Done |
| 9 — Analysis & Documentation | 7 | 4/7 Done |
| **Total** | **50** | **38/50 Done** |
