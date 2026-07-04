# Inconsistencies Log

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.05                                   |
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
| **Status** | 🔲 Deferred — note: a related but separate instance (`docs/PRD.md` §2.3 acceptance criteria and §7.3 `gpu_provider` default, not in the file list above) was fixed in this pass; the files listed here are still untouched. |

---

## 2. TODO Summary Table — Outdated

| Attribute | Detail |
|-----------|--------|
| **Found in** | `TODO.md` §Summary (line 226-237) |
| **Description** | Summary table shows all phases as `0/X Done` while individual task tables show many tasks marked ✅ Done (Phases 1-2 complete, Phase 3 mostly done, Phase 4 partially done). |
| **Impact** | Low — cosmetic; the individual task tables are authoritative. |
| **Resolution** | Update Summary table to reflect actual progress. |
| **Status** | ✅ Resolved — Summary table now reflects actual per-phase progress (37/50 done). |

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

## 4. Additional Providers — llama.cpp Implemented; Ollama Still Out of Scope

| Attribute | Detail |
|-----------|--------|
| **Found in** | `PLAN.md` C3 Component Diagram (§1.3, lines 95-99), C4 Code Structure (§1.4, lines 134-138), ADR-003 (§5, lines 265-266), `INTERFACES.md` §2 (provider implementations table, lines 91-96), `CLAUDE.md` §3 (package layout, lines 46-56) |
| **Also in** | `src/airllm_benchmark/providers/` (`transformers_provider.py`, `llamacpp_provider.py` + `llamacpp_helpers.py` now exist) |
| **Missing from** | Implementation — no `ollama_provider.py` (removed per Inconsistency #1; still intentionally out of scope) |
| **Description** | PLAN.md and INTERFACES.md document three provider implementations: Ollama, Transformers, and llama.cpp. Per TODO.md task 3.5, `LlamaCppProvider` has now been implemented for completeness (wraps `llama_cpp.Llama`, supports local `.gguf` paths and HF-Hub `"repo_id::filename"` identifiers, maps `device` to `n_gpu_layers`, routes HF-Hub fetches through the API Gatekeeper). It is unit-tested (36 tests, 100% coverage on both llamacpp files) but is **not yet wired into `sdk/sdk_helpers.py`'s `create_provider()` factory or `config/experiment.json`** — the benchmark's core GPU/CPU/AirLLM comparison still runs exclusively through Transformers, so no config or SDK changes were made as part of this pass. Ollama remains unimplemented and out of scope; it was intentionally removed (see Inconsistency #1) in favor of Transformers as the GPU provider. |
| **Impact** | Low — the benchmark functions correctly with Transformers as the sole wired provider. `LlamaCppProvider` is available for future use (e.g. a future `experiment.json` provider selection) without further protocol changes. Ollama has no implementation and no near-term plan to add one. |
| **Resolution** | llama.cpp: ✅ implemented per TODO 3.5; wiring into `create_provider()`/config selection deferred to whenever a llama.cpp-backed run is actually needed. Ollama: remains accepted as out of scope — update PLAN.md C3/C4 and ADR-003 to mark ollama specifically (not llama.cpp) as "future extension" if those diagrams are revisited. |
| **Status** | 🟡 Partially Resolved — llama.cpp implemented; Ollama still deferred |
