# Inconsistencies Log

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.07                                   |
| **Created**   | 2026-07-04                             |
| **Purpose**   | Track gaps between docs, interfaces, and TODO |

> Each inconsistency is logged here for resolution later. Items are **not** blockers — they are deferred until the relevant phase.

---

## 1. TODO Summary Table — Outdated

| Attribute | Detail |
|-----------|--------|
| **Found in** | `TODO.md` §Summary |
| **Description** | Summary table showed all phases as `0/X Done` while individual task tables showed many tasks marked ✅ Done. |
| **Impact** | Low — cosmetic; the individual task tables are authoritative. |
| **Resolution** | Update Summary table to reflect actual progress. |
| **Status** | ✅ Resolved — Summary table reflects actual per-phase progress (50/50 done). |

---

## 2. SDK Return Types — Underspecified

| Attribute | Detail |
|-----------|--------|
| **Found in** | `INTERFACES.md` §1 |
| **Description** | `run_benchmark()` returns a bare `dict` with keys `summary`, `chart_paths`, `table_text`. `generate_visualization()` returns `list[str]` (chart paths only) but loses `table_text`. No typed return dataclasses defined. |
| **Impact** | Low — works at runtime but lacks type safety. |
| **Resolution** | Optional: introduce `BenchmarkResult` and `VisualizationResult` dataclasses. Touches the published interface, so needs explicit sign-off. |
| **Status** | 🔲 Deferred |

---

## 3. Additional Providers — llama.cpp Implemented, Not Yet Wired

| Attribute | Detail |
|-----------|--------|
| **Found in** | `PLAN.md` C3/C4 diagrams and ADR-003, `INTERFACES.md` §2 (provider implementations table), `CLAUDE.md` §3 (package layout) |
| **Also in** | `src/airllm_benchmark/providers/` (`transformers_provider.py`, `llamacpp_provider.py` + `llamacpp_helpers.py` exist) |
| **Description** | The docs list two provider implementations: Transformers and llama.cpp. Per TODO.md task 3.5, `LlamaCppProvider` has been implemented for completeness (wraps `llama_cpp.Llama`, supports local `.gguf` paths and HF-Hub `"repo_id::filename"` identifiers, maps `device` to `n_gpu_layers`, routes HF-Hub fetches through the API Gatekeeper). It is unit-tested (36 tests, 100% coverage on both llamacpp files) but is **not yet wired into `sdk/sdk_helpers.py`'s `create_provider()` factory or `config/experiment.json`** — the benchmark's core GPU/CPU/AirLLM comparison runs exclusively through Transformers, so no config or SDK changes were made as part of this pass. |
| **Impact** | Low — the benchmark functions correctly with Transformers as the sole wired provider. `LlamaCppProvider` is available for future use (e.g. a future `experiment.json` provider selection) without further protocol changes. |
| **Resolution** | Wiring `LlamaCppProvider` into `create_provider()`/config selection is deferred to whenever a llama.cpp-backed run is actually needed. |
| **Status** | 🟡 Partially Resolved — llama.cpp implemented; wiring deferred |
