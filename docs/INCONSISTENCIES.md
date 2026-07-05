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

## 2. SDK Return Types — Now Typed

| Attribute | Detail |
|-----------|--------|
| **Found in** | `INTERFACES.md` §1 |
| **Description** | Formerly: `run_benchmark()` returned a bare `dict` with keys `summary`, `chart_paths`, `table_text`. `generate_visualization()` already returned `VisualizationResult` (frozen dataclass). Now: `run_benchmark()` returns a new frozen dataclass `BenchmarkSummaryResult(summary: str, chart_paths: list[str], table_text: str)`. |
| **Impact** | Low — type-safe now; consumers updated to use attribute access. |
| **Resolution** | Introduced `BenchmarkSummaryResult` in `sdk/sdk_summary.py` (co-located with `build_summary()`). Updated `run_benchmark()` to instantiate and return it. Updated single real consumer (`cli_printers.py::print_run_all_result()`). Updated tests and documentation (`INTERFACES.md` §1.1, `CONFIG.md`). All internal type-checking (`# type: ignore[no-untyped-def]` on cli_printers) used where needed. |
| **Status** | ✅ Resolved |

---

## 3. Additional Providers — llama.cpp Implemented, Now Wired

| Attribute | Detail |
|-----------|--------|
| **Found in** | `PLAN.md` C3/C4 diagrams and ADR-003, `INTERFACES.md` §2 (provider implementations table), `CLAUDE.md` §3 (package layout) |
| **Also in** | `src/airllm_benchmark/providers/` (`transformers_provider.py`, `llamacpp_provider.py` + `llamacpp_helpers.py` exist) |
| **Description** | Per TODO.md task 3.5, `LlamaCppProvider` was implemented for completeness (wraps `llama_cpp.Llama`, supports local `.gguf` paths and HF-Hub `"repo_id::filename"` identifiers, maps `device` to `n_gpu_layers`, routes HF-Hub fetches through the API Gatekeeper). It is unit-tested (36 tests, 100% coverage on both llamacpp files). As of this update, it is **now wired into `sdk/sdk_helpers.py`'s `create_provider()` factory** — `create_provider("llamacpp", ...)` instantiates `LlamaCppProvider` with the configured device (formerly only `"transformers"` was supported). `config/experiment.json` now includes an optional `provider_config.llamacpp` block with `device` settings. The benchmark's core GPU/CPU/AirLLM comparison continues to run with Transformers as the default (`gpu_provider`/`cpu_baseline_provider` still set to `"transformers"`), but users can now select llama.cpp by changing these fields to `"llamacpp"`. |
| **Impact** | Low — default benchmark behavior unchanged (Transformers remains default). llama.cpp is now opt-in and functional. |
| **Resolution** | Wiring completed. Added `create_provider()` branch for `"llamacpp"`, config block documentation, and test coverage (`tests/unit/test_create_provider.py`). |
| **Status** | ✅ Resolved |
