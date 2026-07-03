# Inconsistencies Log

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.00                                   |
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
| **Resolution** | Defer to Phase 5 (SDK Layer). Either add as a TODO task or absorb into SDK. |
| **Status** | 🔲 Deferred |

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
