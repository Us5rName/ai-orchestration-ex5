# Inconsistencies Log

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.02                                   |
| **Created**   | 2026-07-04                             |
| **Purpose**   | Track gaps between docs, interfaces, and TODO |

> Each inconsistency is logged here for resolution later. Items are **not** blockers — they are deferred until the relevant phase.

---

## 1. ResultWriter — Architecture vs. TODO

| Attribute | Detail |
|-----------|--------|
| **Found in** | `PLAN.md` C3 Component Diagram (§1.3, line 91) |
| **Also in** | `PLAN.md` Sequence Diagram (§2, lines 180, 199-200) |
| **Missing from** | `INTERFACES.md`, `docs/TODO.md` |
| **Description** | PLAN defines a `ResultWriter` component that serializes `MetricsRecord` → `results/metrics.json`. The Runner Manager calls `append(result)` after each run. This component is never listed as a TODO task, nor does it have an interface definition. |
| **Impact** | Low — `sdk/sdk.py` can handle JSON persistence inline without a dedicated component. |
| **Resolution** | Implemented `services/result_writer.py` with `append()`, `load()`, `clear()`. Added to `INTERFACES.md` §7. Unit tests: `tests/unit/test_result_writer.py` (11 tests). Real-data PoC: `pocs/result_writer_real_data_poc.py`. |
| **Status** | ✅ Resolved |

---

## 2. Ollama References — GPU Provider Changed to Transformers

| Attribute | Detail |
|-----------|--------|
| **Found in** | `CLAUDE.md`, `docs/CONFIG.md`, `docs/INTERFACES.md`, `docs/PLAN.md`, `docs/IMPLEMENTATION.md` |
| **Also in** | `CLAUDE.md` §3 (package layout lines 46-56, API gatekeeper lines 79-80, QA §5 lines 95-96), `docs/CONFIG.md` §2 (example config lines 50-57, field description lines 63-72), `docs/INTERFACES.md` §2 (provider implementations table lines 91-96), `docs/PLAN.md` §1.3 (C3 component diagram lines 95-99, lines 109-115), §1.4 (C4 code structure lines 134-138), §5 (ADR-003 lines 265-266), §6 (deployment lines 319-323), `docs/IMPLEMENTATION.md` (Example: Ollama Provider lines 55-64, Mandatory Standards lines 71-81) |
| **Missing from** | `src/airllm_benchmark/providers/` (no `ollama_provider.py`) |
| **Description** | Per PROMPT_LOG.md Entry 22, the GPU provider was changed from ollama to transformers. `config/experiment.json` was updated (`gpu_provider: "transformers"`), `ollama_provider.py` was removed, and TODO.md was updated. However, multiple documentation files still reference ollama as if it were an active provider: package layout diagrams, config examples, provider implementation tables, component diagrams, code structure diagrams, ADRs, deployment diagrams, and implementation examples. |
| **Impact** | Medium — documentation is misleading; new contributors may assume ollama is still supported. |
| **Resolution** | Update all affected documents to remove ollama references or mark ollama as "removed". Documents to update: `CLAUDE.md` (§3 package layout, §3 API Gatekeeper, §5 QA), `docs/CONFIG.md` (§2 example config and field descriptions), `docs/INTERFACES.md` (§2 provider implementations table), `docs/PLAN.md` (§1.3 C3, §1.4 C4, §5 ADR-003, §6 deployment), `docs/IMPLEMENTATION.md` (Example section, Mandatory Standards). |
| **Status** | 🔲 Deferred

---

## 3. TODO Summary Table — Outdated

| Attribute | Detail |
|-----------|--------|
| **Found in** | `TODO.md` §Summary (line 226-237) |
| **Description** | Summary table shows all phases as `0/X Done` while individual task tables show many tasks marked ✅ Done (Phases 1-2 complete, Phase 3 mostly done, Phase 4 partially done). |
| **Impact** | Low — cosmetic; the individual task tables are authoritative. |
| **Resolution** | Update Summary table to reflect actual progress. |
| **Status** | 🔲 Deferred |

---

## 4. SDK Return Types — Underspecified

| Attribute | Detail |
|-----------|--------|
| **Found in** | `INTERFACES.md` §1 |
| **Description** | `run_benchmark()` returns bare `dict` with keys `summary`, `chart_paths`, `table_text`. `generate_visualization()` returns `list[str]` (chart paths only) but loses `table_text`. No typed return dataclasses defined. |
| **Impact** | Low — works at runtime but lacks type safety. |
| **Resolution** | Defer to Phase 5 (SDK Layer). Consider `BenchmarkResult` and `VisualizationResult` dataclasses. |
| **Status** | 🔲 Deferred |
