# Task Tracking — AirLLM Inference Benchmark

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.00                                   |
| **Based on**  | `docs/PRD.md`, `docs/PLAN.md` v1.00    |
| **Created**   | 2026-07-03                             |

> **TDD Rule:** Tests are written alongside each phase, not after. Each task that produces code includes its tests. Global coverage gate at the end.
> **Dependencies:** `Depends` column lists tasks that must complete first.
> **Integration:** Staged bottom-up. Each phase integrates with the previous before moving on. See [Integration Plan](#integration-plan).
> **AI usage & cost:** AI-assisted engineering and the benchmark's measured (local, $0-API) cost are recorded in [`AI_USAGE_AND_COST.md`](AI_USAGE_AND_COST.md).

---

## Phase 1 — Project Scaffolding

| #  | Task | Status | Definition of Done |
|----|------|--------|-------------------|
| 1.1 | Create project directory structure (`src/`, `tests/`, `config/`, `results/`, `assets/`, `notebooks/`) | ✅ Done | All directories exist; matches PLAN C4 code structure |
| 1.2 | Initialize `pyproject.toml` with dependencies (`airllm`, `transformers`, `psutil`, `pytest`, `matplotlib`, `pandas`, `ruff`) | ✅ Done | `uv sync` succeeds; `uv.lock` generated |
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
| 3.3 | ~~Implement a separate HTTP-client provider~~ | 3.2 | ~~Not Started~~ | **Removed** — Transformers is the wired GPU provider; no separate HTTP-client provider was needed |
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
| **I7** | Real config + real provider (Transformers) + small model | Config loads real JSON; Transformers provider loads the small model; generates text | Verify transformers import; check HF cache |
| **I8** | Real config + real provider (Transformers) + small model on CPU | Transformers provider loads small model on CPU; generates text | Verify no GPU required |
| **I9** | Real provider + real metrics (Transformers) | Same as I7 but metrics collector samples real process memory | Verify psutil readings match system monitor |
| **I10** | Real GPU runner (Transformers + real metrics) | GPU runner executes small model via Transformers; returns real metrics dict | Verify metrics dict matches schema; status = success |
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
| I7 | Real (Transformers) | Small (real) | Mocked | HF Hub |
| I8 | Real (Transformers) | Small (real) | Mocked | HF Hub |
| I9 | Real (Transformers) | Small (real) | Real | HF Hub |
| I10 | Real (Transformers) | Small (real) | Real | HF Hub |
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
| **CP7** (after I7) | Real Transformers provider returns text for small model | `uv run python src/main.py --single --provider transformers --model small` |
| **CP8** (after I8) | Real Transformers provider returns text for small model on CPU | `uv run python src/main.py --single --provider transformers --model small` |
| **CP9** (after I10) | GPU runner (Transformers) returns valid metrics for small model | `uv run python src/main.py --single --mode gpu --model small` |
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
| 7.1 | Handle gated model access — accept HuggingFace terms for Llama models | 1.3 | ✅ N/A — resolved, no action needed | **Moot.** `docs/PRD.md` §7.1's model-selection table names `meta-llama/Llama-3.2-1B` as the illustrative "small" tier example, but the *actual* configured models in `config/experiment.json` are all open, ungated Qwen checkpoints (`Qwen/Qwen2.5-0.5B-Instruct`, `Qwen/Qwen2.5-3B-Instruct`, `Qwen/Qwen2.5-7B-Instruct`) — confirmed by inspection 2026-07-04. None require HF gated-access term acceptance. A separate PR's CI run independently hit a 401 from `meta-llama/Llama-3.2-1B` with no `HF_TOKEN` configured, which is what prompted this check — but that model is not referenced anywhere the benchmark actually runs. No programmatic term-acceptance was attempted (that requires a human to click "Agree" on huggingface.co); none was needed. If a gated model is reintroduced later, the user must visit its HF page, accept terms, and set `HF_TOKEN` in `.env` before this task can be closed the "real" way. |
| ⚠️ | | | | **Caution:** Gated models (Llama) require manual term acceptance on HuggingFace before any API access works. Not applicable to the current config. |
| 7.2 | Pre-download all models to HF cache | 7.1 | ✅ Done (small, medium, large all cached) | All three configured tiers loaded end-to-end (`load_model` → `generate` → `unload`) through `TransformersProvider` on 2026-07-04: `Qwen/Qwen2.5-0.5B-Instruct` (small, ~2.27 GB, ~3.4s), `Qwen/Qwen2.5-3B-Instruct` (medium, ~6.18 GB, ~61s incl. download), `Qwen/Qwen2.5-7B-Instruct` (large, ~15.24 GB, ~143s incl. download). Verified present via `huggingface_hub.scan_cache_dir()` (26.17 GB total cache). Network access confirmed working in this sandbox (no CUDA available here — driver too old for the installed torch build — so loads used `device="cpu"`; that's sufficient for caching weights, which is this task's goal). The large tier at the time of this pre-cache step was `Qwen2.5-7B`; it was later repinned to `Qwen2.5-32B-Instruct` (task 8.3 / benchmark execution), whose weights were fetched during the AirLLM run. No 72B model was ever in scope, so the "~140 GB / verify disk space" caution below does not apply as originally written. |
| ⚠️ | | | | **Caution:** Original caution assumed a 72B model; the largest tier is `Qwen2.5-32B` (~65.5 GB unquantized). Disk was not a constraint (1.6 TB free). |
| 7.3 | Fill in `config/hardware.json` with actual machine specs | 2.2 | ✅ Done | All fields populated; no empty values |
| 7.4 | POC: config + provider validation | 2.3, 3.3, 3.4, 7.2, 7.3 | ✅ Done | Reused existing `validate_config()`/`validate_hardware()` in `shared/config_loader.py` rather than duplicating. Added `BenchmarkSDK.validate()` (`sdk/sdk_validation.py`, `ValidationResult`) which: (1) loads + validates `experiment.json`/`hardware.json`, never raising — failures are captured in `ValidationResult.config_error`; (2) instantiates each configured provider (`gpu_provider`, `cpu_baseline_provider`) via the existing `create_provider()` factory with **no** `load_model()`/`generate()` call, so no inference runs; (3) reports HF-cache presence per model via new `shared/cache_check.py::model_cache_status()` (`huggingface_hub.scan_cache_dir()`) — informational only, does not fail validation. Wired into CLI as `uv run python src/main.py --validate` (see `docs/INTERFACES.md` §10). Unit tests in `tests/unit/test_sdk_validation.py`, `tests/unit/test_cache_check.py`, `tests/unit/test_cli_validate.py` — all external calls mocked, no real downloads. Manually verified against the real cached models: reports PASSED with all three tiers cached. |
| ⚠️ | | | | **Caution:** This step catches misconfiguration before expensive benchmark runs. Do not skip. |

---

## Phase 8 — Benchmark Execution

| #  | Task | Depends | Status | Definition of Done |
|----|------|---------|--------|-------------------|
| 8.1 | GPU smoke test — small model, verify GPU inference | 7.4 | ✅ Done | Runs via Transformers per `gpu_provider` config. `Qwen/Qwen2.5-0.5B-Instruct` on real CUDA (RTX 3090, `torch==2.6.0+cu124` — see 12.x fix below): load 0.16s, TTFT 3.01s, total 3.80s, 40.1 tok/s, peak RAM 810MB, peak VRAM 966MB. Status success. |
| 8.2 | Run GPU baseline — small model via configured provider | 8.1 | ✅ Done | Same run as 8.1 (single-prompt smoke test doubled as the baseline given the tiny model). Recorded in `results/metrics_phase8.json`. |
| 8.3 | Run CPU baseline — large model via configured CPU provider | 8.2 | ✅ Done | `config/experiment.json`'s `"large"` tier repinned from `Qwen2.5-7B` to `Qwen2.5-32B-Instruct` (~65.5GB unquantized fp16) — the 7B/4bit original comfortably fit this sandbox's 62GB RAM, which would not have demonstrated OOM/slowness at all (see PROMPT_LOG Entry 58). Run raw/unquantized under an external memory-and-timeout watchdog (this sandbox has 0 swap, so an uncontrolled OOM hits the kernel killer directly). **Result: timeout** — killed after the 15-minute wall-clock limit, peak RAM 38.6GB (still climbing toward ~65.5GB, never reached generation). Process was in Linux `D` state (uninterruptible `filemap_fault` — mmap page-in stalling under memory pressure) when the watchdog's own timeout fired; the orphaned worker (spawned as a grandchild by `uv run`, outliving the watchdog's direct-child kill) had to be killed directly by PID. This **is** the PRD's "OOM or extreme slowness" outcome — a clean demonstration that raw CPU loading cannot handle this model size on this hardware. |
| ⚠️ | | | | **Caution:** This run may crash or hang. Set a timeout. If it hangs, kill the process and record the timeout as the result. — Confirmed accurate: it hung, and the timeout path is exactly what was needed. |
| 8.4 | Run AirLLM — same large model via AirLLM | 8.3 | ✅ Done | `Qwen/Qwen2.5-32B-Instruct` via AirLLM, 4-bit paged inference: load/TTFT 604.31s (17-shard download + per-layer 4bit conversion), total 1069.60s, 0.1 tok/s, peak RAM 6933MB, peak VRAM 1924MB. Status success — succeeds in ~6.9GB RAM where raw loading needs ~65GB (and still hadn't finished loading at 38.6GB after 15 minutes per 8.3), demonstrating AirLLM's value proposition directly (steep latency trade-off, as expected). |
| ⚠️ | | | | **Caution:** AirLLM with a large model on CPU will be slow. Monitor RAM usage. If system becomes unresponsive, reduce model size or increase quantization. |
| 8.5 | POC: full benchmark pipeline | 8.4 | ✅ Done | All three real scenarios (GPU baseline, AirLLM, CPU baseline) run end-to-end and persisted to `results/metrics_phase8.json` via `ResultWriter`; no mocks. |
| 8.6 | Generate visualizations — charts + comparison table | 8.5 | ✅ Done | `Visualizer.generate_all()` / `generate_table()` over `results/metrics_phase8.json` → `assets/phase8/latency_chart.png`, `assets/phase8/memory_chart.png`, and a comparison table. Memory chart is the clearest evidence: CPU baseline (38.6GB, still climbing) vs. AirLLM (6.9GB, complete) vs. GPU baseline (810MB). |
| 8.7 | Run GPU baseline — medium model (3B) | 8.2 | ✅ Done | `Qwen/Qwen2.5-3B-Instruct` GPU baseline via Transformers (P1/P2/P3 unquantized): average runtime 5.47s, 32 tokens per prompt, 5.8 tok/s average throughput. Peak RAM 4.6 GB average, peak VRAM ~3.2 GB. Recorded in `results/metrics_medium.json`. Visualizations in `assets/medium/latency_chart.png`, `assets/medium/memory_chart.png`. **Rationale:** PRD.md §4.3 names the medium tier a "good AirLLM comparison target"; it was cached (task 7.2) but never benchmarked until now. Results added to README Results table. |

---

## Phase 9 — Analysis & Documentation

| #  | Task | Depends | Status | Definition of Done |
|----|------|---------|--------|-------------------|
| 9.1 | Create `notebooks/analysis.ipynb` — Jupyter notebook with results analysis | 8.6 | ✅ Done | Loads `results/metrics_phase8.json` into a `pandas.DataFrame` (no hardcoded numbers — every figure/table is computed from the JSON, including the unquantized-model-size figure parsed from the CPU-baseline `error` string via regex); reuses `services/visualizer.py::Visualizer`/`MetricsRecord` for the comparison table; embeds the existing `assets/phase8/*.png` charts plus two additional inline matplotlib charts (log-log latency-vs-memory scatter, time/memory cost bars); LaTeX formulas for throughput, AirLLM memory-reduction ratio, and a latency-memory efficiency score; a cost & resource analysis section (time/memory, no dollar cost); a sensitivity-analysis/limitations section documenting the single-run-per-scenario constraint and a future sweep design over `config/experiment.json`'s `P1`/`P2`/`P3` prompts, quantization levels, and `max_new_tokens`; academic references (AirLLM repo, HF Transformers, QLoRA/NF4 arXiv:2305.14314 and LLM.int8() arXiv:2208.07339 — the actual `bitsandbytes` mechanisms behind `providers/transformers_helpers.py::build_quant_config`, not a generic placeholder — and the Qwen2.5 technical report arXiv:2412.15115). Executes clean top-to-bottom via `uv run jupyter nbconvert --to notebook --execute --inplace notebooks/analysis.ipynb` (jupyter/nbconvert/ipykernel added as `dev` extras in `pyproject.toml`). |
| 9.2 | Verify global test coverage ≥ 85% | 2.4, 3.6, 4.2, 4.5, 5.8 | ✅ Done | `uv run pytest --cov` passes (89.6%); coverage report generated; gated in CI |
| 9.3 | Run `ruff check` — zero violations | 6.2 | ✅ Done | `uv run ruff check` returns 0 (`src tests scripts`); gated in CI |
| 9.4 | Verify no file exceeds 150 lines | 6.2 | ✅ Done | All `.py` files ≤ 150 lines; gated in CI via `scripts/check_line_cap.py` |
| 9.5 | Update `README.md` — installation, usage, configuration, examples | 8.6 | ✅ Done | Full README with overview, architecture diagrams, results, cost, quick start, and a hand-maintained repository-facts section |
| 9.6 | `tests/integration/test_pipeline.py` — full pipeline smoke test | 5.7 | ✅ Done | Drives `BenchmarkSDK.run_single()` (real entry point, not mocked) end-to-end with a real `Qwen/Qwen2.5-0.5B-Instruct` via `TransformersProvider` on CPU (isolated `experiment.json` fixture keeps `max_new_tokens` tiny); asserts `MetricsRecord.status == "success"` plus timing/token/RAM invariants; 1 test, runs in ~11s |
| 9.7 | Run final checklist per [`final-checklist`](.agents/skills/final-checklist/SKILL.md) | 9.2, 9.3, 9.4, 9.5 | ✅ Done | Ran all 6 checklist sections. Fixed on the spot: 2 missing `__init__` docstrings (`transformers_provider.py`, `llamacpp_provider.py`); CI now uploads an HTML coverage report as a build artifact (`.github/workflows/ci.yml`); added a `## Attribution` section to `README.md` crediting AirLLM, Qwen2.5, HF Transformers, bitsandbytes, llama.cpp. All 10 gate scripts + full `pytest --cov` (338 passed, 1 skipped, 93.36%) re-verified green after fixes. Two items intentionally left open (not silently marked done): no `LICENSE` file (license choice needs an explicit decision, not assumed); no formal ISO/IEC 25010 mapping doc (checklist item, never required by this project's own PRD/PLAN/TODO). **Parameter sweep now executed** (feature branch item #3): P1/P2/P3 × {8, 32, 128} tokens on GPU baseline (9 runs, unquantized only — 4bit/8bit quantization too expensive). Results in `results/metrics_sweep.json`; integrated into `notebooks/analysis.ipynb` §5 with pivot-table and chart analysis. "Parallel processing with thread safety" is N/A by design — `shared/gatekeeper.py` documents that the benchmark is intentionally single-threaded so peak-memory measurements per run stay uncontaminated. |

---

## Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| 1 — Scaffolding | 4 | 4/4 Done |
| 2 — Configuration | 5 | 5/5 Done |
| 3 — Providers | 9 | 9/9 Done (3.3 removed, excluded from count) |
| 4 — Services | 5 | 5/5 Done |
| 5 — SDK (Runners) | 8 | 8/8 Done |
| 6 — CLI | 2 | 2/2 Done |
| 7 — Pre-Benchmark | 4 | 4/4 Done (7.1 resolved as N/A — see task note) |
| 8 — Benchmark Execution | 6 | 6/6 Done |
| 9 — Analysis & Documentation | 7 | 7/7 Done |
| **Total** | **50** | **50/50 Done** |

---

## Phase 10-b — E2E Verification & Gap Remediation

**Preamble:** A comprehensive end-to-end connectivity audit conducted 2026-07-05 to verify that every layer (CLI → SDK → Runner → Provider → Services → results/assets) is actually wired and exercised in production code paths, not just in mocked unit tests. Three exploration passes (docs/TODO/phase status, test/CI coverage, SDK/provider/runner wiring) identified 9 concrete gaps between "implemented" and "actually reachable." This phase documents findings and creates actionable remediation tasks.

### Verification Results

| Verification Step | Result | Details |
|---|---|---|
| **Environment setup** | ✅ Pass | `uv sync --all-extras` installed pytest, coverage; all deps ready |
| **Ruff (linting)** | ✅ Pass | 0 violations across `src/`, `tests/`, `scripts/` |
| **Line cap (≤150 lines/file)** | ✅ Pass | All files comply |
| **validate_repo.py** | ✅ Pass | 3/3 project-specific checks pass |
| **Secret scanning** | ✅ Pass | No generic patterns or banned files found |
| **Docs present** | ✅ Pass | All 12 required documentation files present |
| **Markdown links** | ✅ Pass | All internal file-path links resolve |
| **No tracked archives** | ✅ Pass | No tar/gz/zip in git |
| **Planning IDs unique** | ✅ Pass | 50 unique task IDs, no duplicates |
| **Workflow permissions minimal** | ✅ Pass | All CI workflows have minimal permissions declared |
| **Unit test suite** | ✅ Pass | 265 tests passed, 0 failed |
| **Test coverage** | ✅ Pass | 91.41% coverage (exceeds 85% requirement) |
| **CLI --validate (dry-run)** | ✅ Pass | Loads config, validates providers, checks model cache, returns summary |
| **CLI --single (real inference)** | ✅ Pass | Real CPU inference: loaded 0.5B model, generated 32 tokens in 9.47s, collected MetricsRecord |

### Gaps Found & Remediation Tasks

| # | Task | Description | Status |
|----|------|-------------|--------|
| 10.1 | **Llamacpp provider is orphaned** | `providers/llamacpp_provider.py` + `llamacpp_helpers.py` are fully implemented, protocol-compliant, gatekeeper-wired, and unit-tested (36 tests, 100% coverage). However, `config/experiment.json` and every production script (`scripts/run_*.py`) hardcode `"transformers"` as the provider. The `llamacpp` branch in `sdk/sdk_helpers.py::create_provider()` is dead code — never reachable from any config/script path, only via unit tests or manual `create_provider("llamacpp", ...)` calls. **Decision:** Expose llamacpp as an opt-in comparison run rather than a config default — `scripts/run_llamacpp_benchmark.py` calls `BenchmarkSDK.run_single(..., provider="llamacpp")` explicitly for the small tier (official `Qwen/Qwen2.5-0.5B-Instruct-GGUF` q4_k_m quant, added as `models.small_gguf` in `config/experiment.json`); `gpu_provider`/`cpu_baseline_provider` stay `"transformers"` by default. Results in `results/metrics_llamacpp.json`, charts in `assets/llamacpp/`. **Environment caveat:** on this machine the installed `llama-cpp-python` wheel has no CUDA backend compiled in (a CUDA-enabled prebuilt wheel was tried and crashed with SIGILL — likely an AVX512/CPU-microarch mismatch in that wheel), so despite `provider_config.llamacpp.device = "cuda"`, these runs actually executed on CPU (`peak_vram_mb` is `0.0` for all three; `peak_ram_mb` ~0.65–1.1GB). This is disclosed in the README results row rather than mislabeled as a GPU run. | ✅ Resolved |
| 10.2 | **ResultWriter class bypassed by benchmark scripts** | `services/result_writer.py` is fully documented (INTERFACES.md §7), tested (100% coverage), and production-code-ready. However, both `scripts/run_medium_benchmark.py` (lines 69–71) and `scripts/run_param_sweep.py` (lines 80–82) bypass it entirely, hand-rolling their own `dataclasses.asdict(record) → json.dump()` logic instead. This is a DRY violation against CLAUDE.md §4. The actual committed `results/metrics_medium.json` and `results/metrics_sweep.json` were never produced by the documented ResultWriter code path. **Fix:** Route both scripts through `ResultWriter` instead of duplicating serialization. | 🔄 Pending |
| 10.3 | **Visualizer never invoked by benchmark scripts** | `services/visualizer.py` is fully implemented (100% coverage) and documented (INTERFACES.md §6). Charts for `assets/phase8/*.png` were generated by the notebook (`notebooks/analysis.ipynb` imports and calls `Visualizer`). However, the committed script `scripts/run_medium_benchmark.py` never calls `Visualizer` — despite producing `assets/medium/latency_chart.png` and `assets/medium/memory_chart.png` that exist in the repo. These were generated out-of-band (manually in a REPL) and committed alongside. **Result:** Running `run_medium_benchmark.py` today cannot reproduce its own charts. **Fix:** Add `Visualizer` invocation to both `run_medium_benchmark.py` and `run_param_sweep.py` so charts are reproducible from the committed script. | 🔄 Pending |
| 10.4 | **generate_visualization() has no CLI entry point** | `BenchmarkSDK.generate_visualization()` (sdk/sdk.py, lines 126–140) is fully implemented, tested, and documented (INTERFACES.md §1). It is reachable only programmatically (via the notebook) or by direct SDK instantiation — no `main.py` flag exposes it. Users cannot invoke visualization from the CLI. **Fix:** Added a `--visualize` flag to `src/main.py`, dispatched via `cli_dispatch.add_visualize_arguments` / `run_visualize` and printed via `cli_printers.print_visualization_result` (mirroring the existing `--report` pattern). It loads persisted records from `--results-path` (default `results/metrics.json`, per CONFIG.md §1) via `ResultWriter.load()`, then calls `BenchmarkSDK.generate_visualization(records, output_dir=...)`, printing chart paths and the comparison table. Usable as `uv run python src/main.py --visualize --results-path results/metrics_medium.json --config-dir <dir>`. Unit-tested in `tests/unit/test_cli_visualize.py` with SDK and ResultWriter mocked; manually verified end-to-end against a committed results file. | ✅ Resolved |
| 10.5 | **cache_check.py undocumented in INTERFACES.md** | `shared/cache_check.py` is fully wired into `sdk_validation.py` (lines 15, 79) and used by `BenchmarkSDK.validate()` (the dry-run path). It is documented in `docs/TODO.md` (task 7.4) and `docs/PROMPT_LOG.md` but is missing from `docs/INTERFACES.md` — the "holy" contract document per CLAUDE.md §1. This violates the documentation-as-contract discipline. **Fix:** Add a new section (§11 or equivalent) in `docs/INTERFACES.md` documenting the `model_cache_status()` function and the `CacheCheckResult` dataclass. | 🔄 Pending |
| 10.6 | **CP1–CP12 checkpoint table outdated** | `docs/TODO.md`'s Integration Plan section references test filenames that no longer exist in the codebase (e.g., `test_config.py`, `test_providers.py` partially, `test_metrics.py`, `test_visualizer.py`, `test_runners.py`). The unit test suite was split into many more granular files (`test_config_loader.py`, `test_config_real_experiment.py`, `test_config_real_hardware.py`, `test_metrics_collector.py`, `test_metrics_sampler.py`, `test_visualizer_charts.py`, `test_gpu_runner.py`, etc.). Additionally, CP12 is defined twice (once for I13 / phase 7, once for I14 / phase 7.x — a numbering bug). **Fixes:** (a) Update all test-filename references in the checkpoint table to match current split-up test files. (b) Renumber the duplicate CP12 to CP13 or consolidate the checkpoints. | 🔄 Pending |
| 10.7 | **Integration tier lacks GPU and AirLLM coverage** | `tests/integration/` contains exactly one real E2E test: `test_pipeline.py::test_full_pipeline_cpu_smoke` — CPU-only, validates `BenchmarkSDK.run_single()` end-to-end with a real 0.5B model and `TransformersProvider` on CPU. There is no integration-tier (as opposed to POC-tier) E2E test that exercises the GPU runner or the AirLLM runner end-to-end under real conditions. GPU and AirLLM coverage currently exists only in `tests/pocs/`, which is documented as proof-of-concept work, not the integration suite. **Fix:** Add GPU and/or AirLLM integration tests under `tests/integration/` that follow the same pattern as `test_full_pipeline_cpu_smoke` (real SDK invocation, real model, real provider) but exercise GPU/AirLLM paths. | 🔄 Pending |
| 10.8 | **LICENSE file decision still pending** | Noted in Phase 9 task 9.7 as deliberately left open: "license choice needs an explicit decision, not assumed." No `LICENSE` file is checked into the repo. **Action:** Decide on a license (MIT, Apache 2.0, etc.) and create the file, or confirm that the project is intentionally unlicensed and document that decision in a comment. | 🔄 Pending decision |
| 10.9 | **ISO/IEC 25010 mapping never written** | Noted in Phase 9 task 9.7 as intentionally deferred: "checklist item, never required by this project's own PRD/PLAN/TODO." No ISO/IEC 25010 software-quality mapping doc exists. Per the project's own rules, this is not required — but it was a checklist item. **Action:** Confirm whether this is still intentionally out-of-scope or should be added as a reference doc. | 🔄 Pending decision |

**Summary:** 9 gaps identified. No critical bugs found — the happy path (Transformers provider, CPU/GPU/AirLLM runners, SDK, CLI) is fully wired and works end-to-end. All gaps are either orthogonal concerns (orphaned but harmless code, documentation gaps, missing CLI flags) or minor DRY violations (duplicate serialization). Remediation tasks are non-blocking and can be tackled in order of priority; none involve architectural rework.

---

## Phase 11 — Additive Reporting Layer (BENCHMARK.md §5)

**Preamble:** `docs/BENCHMARK.md` §5 required an 8+-column comparison table, six charts (V1–V6, 300 DPI, value labels, OOM annotation, hardware-RAM reference line), CSV export, and a hardware-aware narrative summary — beyond what the existing `Visualizer` (2 charts, 5-column table) provides. This phase adds a new, additive reporting layer without changing any existing interface, signature, or behavior.

| # | Task | Status |
|----|------|--------|
| 11.1 | `services/report_helpers.py` — tier lookup, tier/mode grouping, fixed `MODE_COLORS` (GPU=blue, CPU=orange, AirLLM=green per §5.2) | ✅ Done |
| 11.2 | `services/report_tables.py` — full §5.1 comparison table + `export_metrics_csv` (18 fields + derived `tier`) | ✅ Done |
| 11.3 | `services/report_chart_core.py` — shared 300-DPI grouped/stacked bar renderer (value labels, OOM hatch, reference line) | ✅ Done |
| 11.4 | `services/report_charts.py` (V1–V3) + `services/report_charts_extra.py` (V4–V6) | ✅ Done |
| 11.5 | `services/report_builder.py` + `services/report_narrative.py` — `ReportBuilder`, `ReportResult`, `build_narrative_summary`, `derive_report_output_dir` | ✅ Done |
| 11.6 | `BenchmarkSDK.generate_report()` (via `sdk/sdk_report_helpers.py` to keep `sdk.py` ≤150 lines) + `--report`/`--assets-dir` CLI flags (`cli_dispatch.py`, `cli_printers.print_report_result`) | ✅ Done |
| 11.7 | `docs/INTERFACES.md` §11, `docs/CONFIG.md` CSV note | ✅ Done |
| 11.8 | Tests: `test_report_tables.py`, `test_report_charts.py`, `test_report_builder.py`, `fixtures_report.py` | ✅ Done |

**Out of scope (documented as caveats, not implemented):** warm/cold load distinction, download-time-separate-from-load, GPU VRAM numeric capacity reference line, V5 prompt-sensitivity chart on current archived results (all existing `results/*.json` have empty `prompt_id`; the chart renders once future runs populate it, and skips gracefully otherwise). See the original plan for the full rationale table.

**Non-breakage:** `MetricsRecord`, `table_helpers.format_comparison_table`, `chart_helpers.*`, `visualizer.Visualizer.*` (incl. `generate_all` → still exactly 2 paths), `result_writer.ResultWriter`, `sdk_summary.build_summary` — zero changes. `run_benchmark()`'s 2-chart path is unaffected; the full report is opt-in via `--report`.

---

## Phase 12 — Metrics & Chart Bug Fixes (2026-07-05)

**Preamble:** A real E2E pass (GPU + CPU-baseline single runs, `--report`, and a partial `--run-all`
against actual hardware — RTX 3090, real Qwen2.5 checkpoints) surfaced three defects: `ttft_s`
silently measured setup time instead of first-token latency, the latency chart's linear y-axis
made GPU/AirLLM bars unreadable next to CPU-raw's much larger values, and no chart existed for
`peak_vram_mb` despite it being fully collected and tabulated (flagged as out-of-scope caveat in
Phase 11). Fixed in place; no interface behavior removed, only corrected/extended.

| # | Task | Status |
|----|------|--------|
| 12.1 | Real TTFT: optional `_on_first_token` hook (duck-typed like `_on_download_complete`, not a protocol change) wired through `gpu_runner.py`/`cpu_runner.py`; `transformers_provider.py` fires it via a `StoppingCriteria` (`transformers_helpers.py::FirstTokenCallback`, `build_generate_kwargs`); `MetricsCollector.mark_first_token()`; `assemble_record` now computes real `ttft_s` or `0.0` (unmeasured) instead of approximating from load/setup time. `docs/INTERFACES.md` §5, `docs/CONFIG.md` §1 updated. | ✅ Done |
| 12.2 | Log-scale latency charts: `render_grouped_bar_chart(..., log_scale=True)` in `report_chart_core.py`, applied to V1 (`report_charts.py::render_latency_by_tier_chart`); legacy `chart_helpers.py::render_latency_chart` (`_render_bar_chart(..., log_scale=True)`) gets the same treatment since `run_benchmark()`/`--run-all` still goes through the old `Visualizer`. | ✅ Done |
| 12.3 | New V2b VRAM-by-tier chart: `report_charts.py::render_vram_by_tier_chart` (mirrors V2, groups on `peak_vram_mb`, "Total VRAM" reference line from new `hardware.json` field `vram_gb`); wired into `ReportBuilder.build()`. Numbered "V2b" (not "V7") to match `docs/BENCHMARK.md`'s chart spec (PR #12, `Us5rName/Lahav Tsur`) — a new V7 (`report_charts_scatter.py::render_vram_vs_throughput_scatter`, `peak_vram_mb` vs throughput, mirrors V6) was added alongside it, factored through a shared `_render_scatter_by_mode` helper. `docs/INTERFACES.md` §11 (now "V1-V7 + V2b"/"eight charts"), `docs/CONFIG.md` §3 updated. | ✅ Done |
| 12.4 | Tests + full suite: `test_metrics_collector.py` (+ split `test_metrics_collector_ttft.py`), `test_metrics_edge_cases.py`, `test_gpu_runner_delegation.py`, `test_cpu_runner_delegation.py`, `test_transformers_generate.py`, `test_visualizer_charts.py`, `test_report_charts.py` (+ split `test_report_charts_vram_and_scale.py`), `test_config_models.py`, `test_config_loader.py`, `test_config_real_hardware.py`, `fixtures_report.py` (new `report_hardware` fixture) extended/added/split (150-line cap). 305 passed, 91.56% coverage, ruff = 0, line cap passed. | ✅ Done |

**Verification:** Re-ran the same real E2E commands used to find the bugs. GPU medium-tier single run: `ttft_s` dropped from the buggy 4.61s to a real 0.44s (throughput 15.2 tok/s implies ~65ms/token, consistent with a sub-second prefill). `--report` on a small-tier GPU-vs-CPU-baseline result set (GPU ~4-6s, CPU-raw ~139s) rendered the latency chart with both bars visible on a log axis (previously CPU-raw would flatten GPU/AirLLM to invisibility on a linear axis), and produced `vram_by_mode.png` with a 24GB reference line.

**Non-breakage:** `InferenceProvider` protocol (`providers/base.py`) unchanged — the TTFT hook follows the existing `_on_download_complete` duck-typing precedent, not a signature change. `HardwareConfig` gained a required `vram_gb` field (all committed `config/hardware.json`/`tests/config/hardware.json` fixtures updated accordingly).
