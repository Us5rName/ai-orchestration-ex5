# Inconsistencies Log

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.03                                   |
| **Created**   | 2026-07-04                             |
| **Purpose**   | Track gaps between docs, interfaces, and TODO |

> Each inconsistency is logged here for resolution later. Items are **not** blockers — they are deferred until the relevant phase.

---

## 1. Ollama References — GPU Provider Changed to Transformers

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

## 2. TODO Summary Table — Outdated

| Attribute | Detail |
|-----------|--------|
| **Found in** | `TODO.md` §Summary (line 226-237) |
| **Description** | Summary table shows all phases as `0/X Done` while individual task tables show many tasks marked ✅ Done (Phases 1-2 complete, Phase 3 mostly done, Phase 4 partially done). |
| **Impact** | Low — cosmetic; the individual task tables are authoritative. |
| **Resolution** | Update Summary table to reflect actual progress. |
| **Status** | 🔲 Deferred |

---

## 3. SDK Return Types — Underspecified

| Attribute | Detail |
|-----------|--------|
| **Found in** | `INTERFACES.md` §1 |
| **Description** | `run_benchmark()` returns bare `dict` with keys `summary`, `chart_paths`, `table_text`. `generate_visualization()` returns `list[str]` (chart paths only) but loses `table_text`. No typed return dataclasses defined. |
| **Impact** | Low — works at runtime but lacks type safety. |
| **Resolution** | Defer to Phase 5 (SDK Layer). Consider `BenchmarkResult` and `VisualizationResult` dataclasses. |
| **Status** | 🔲 Deferred |

---

## 4. Additional Providers — Out of Scope

| Attribute | Detail |
|-----------|--------|
| **Found in** | `PLAN.md` C3 Component Diagram (§1.3, lines 95-99), C4 Code Structure (§1.4, lines 134-138), ADR-003 (§5, lines 265-266), `INTERFACES.md` §2 (provider implementations table, lines 91-96), `CLAUDE.md` §3 (package layout, lines 46-56) |
| **Also in** | `src/airllm_benchmark/providers/` (only `transformers_provider.py` exists) |
| **Missing from** | Implementation — no `ollama_provider.py`, no `llamacpp_provider.py` |
| **Description** | PLAN.md and INTERFACES.md document three provider implementations: Ollama, Transformers, and llama.cpp. Only `TransformersProvider` is implemented. `create_provider()` in `sdk_helpers.py` raises `ValueError` for any provider other than `"transformers"`. The additional providers are out of scope for the current exercise — the benchmark focuses on comparing GPU (via Transformers), CPU baseline (via Transformers), and AirLLM paged inference. Ollama and llama.cpp providers are documented as planned components but are not required for the benchmark's core comparison. |
| **Impact** | Low — the benchmark functions correctly with Transformers as the sole provider. The provider abstraction layer exists and can accommodate additional providers when in scope. |
| **Resolution** | Accept as out of scope. Update PLAN.md C3/C4, INTERFACES.md §2, and ADR-003 to explicitly mark ollama and llamacpp as "future extension" rather than required components. Keep `InferenceProvider` protocol intact for extensibility. |
| **Status** | 🔲 Deferred |
