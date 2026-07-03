# Prompt Log — AirLLM Inference Benchmark

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.00                                   |
| **Session**   | 2026-07-03                             |
| **Purpose**   | Track prompts, decisions, improvements |

---

## Entry 1 — PRD Creation

**Prompt:** Create a PRD for the AirLLM benchmarking assignment.

**Context:** Assignment requires demonstrating AirLLM helps in specific cases. Two levels: "Safe Pass" (functional pipeline, basic metrics) and "High Achiever" (comparative analysis, OOM demonstration).

**Decision:** Created `docs/PRD.md` covering both levels with:
- Three memory scenarios (GPU baseline, CPU raw failure, AirLLM success)
- Model tiers (small 1B, medium 7B, large 72B)
- Metrics: TTFT, peak RAM, runtime, tokens/second
- Hardware documentation requirement (no invented specs)

**Improvement:** User flagged hardcoded time targets (< 30s, < 120s). Removed — benchmarks should speak for themselves. Added hardware specs section with fill-in fields.

---

## Entry 2 — Hardware Documentation

**Prompt:** "There shouldn't be times in the target. do you understand why?"

**Context:** Hardcoded latency targets are meaningless across different hardware. Benchmarks should be measured, not predetermined.

**Decision:** Removed all time targets from KPIs and NFRs. Added `docs/PRD.md` §6.1 Benchmarking Hardware with fill-in table (CPU, GPU, RAM, Disk, OS).

**Improvement:** User said "do not invent hardware, just make sure it will be written down." Removed example values — table now says "(document actual)" for each field.

---

## Entry 3 — PLAN Creation

**Prompt:** "Now write a plan"

**Context:** PRD approved. Need architecture document per SDLC.

**Decision:** Created `docs/PLAN.md` with:
- C4 Context, Container, Component, Code diagrams
- Sequence diagram for benchmark execution
- Data schema (metrics record, config files)
- SDK API contract (BenchmarkSDK)
- 5 ADRs (SDK-first, JSON storage, separate runners, config via JSON+.env, psutil monitoring)
- Deployment model, error handling, testing strategy

---

## Entry 4 — Provider-Agnostic Architecture

**Prompt:** "There are more inference providers except ollama, some (including ollama) allow for cpu only runs. how do you suggest we move forward with the documents?"

**Context:** Ollama supports both GPU and CPU. Other providers exist (Transformers, llama.cpp, GPT4All). Current docs assume Ollama=GPU which is incorrect.

**Decision:** Proposed revisions:
- Rename modes to memory scenarios (not provider-specific)
- Add inference provider section to PRD
- Make runners provider-configurable in PLAN
- Clarify comparison is about memory fit, not providers

**Improvement:** User approved. Implemented fixes across both PRD and PLAN.

---

## Entry 5 — Provider Configurability

**Prompt:** "implement the fixes"

**Context:** Apply provider-agnostic changes to both documents.

**Changes:**
- PRD §1.1: Renamed modes → memory scenarios
- PRD §3.2: "Ollama Smoke Test" → "GPU Baseline Smoke Test"
- PRD §6.3: New Inference Providers table
- PRD Glossary: Updated Ollama definition
- PLAN C4 diagrams: "Ollama Server" → "Inference Providers"
- PLAN code structure: `ollama_runner.py` → `provider_runner.py`
- PLAN metrics: Added `provider` field
- PLAN config: Added `gpu_provider` + `provider_config`
- PLAN SDK API: Added `provider` parameter
- PLAN ADR-003: Rewritten for configurable GPU provider
- PLAN error handling: "Ollama server" → "Configured provider"

---

## Entry 6 — CPU Runner Configurability

**Prompt:** "is the cpu_runner also configurable?"

**Context:** GPU runner is provider-configurable. Should CPU baseline runner also be configurable?

**Decision:** Yes — providers like Transformers, llama.cpp, Ollama (CPU mode) can all run on CPU. Made CPU runner provider-configurable.

**Prompt:** "Please make it flexible. and add a providers directory"

**Changes:**
- PLAN: Added `providers/` directory with `base.py`, `ollama_provider.py`, `transformers_provider.py`, `llamacpp_provider.py`
- PLAN: Updated component diagram with providers boundary
- PLAN: Both `gpu_runner` and `cpu_runner` delegate to providers
- PLAN: Config added `cpu_baseline_provider` key
- PLAN: ADR-003 rewritten as "Providers Layer with Configurable Runners"
- PLAN: Added `InferenceProvider` protocol
- PRD §7.3: New Provider Selection table
- PRD §7.4: Metrics protocol now iterates `(model, mode, provider, prompt)`

---

## Entry 7 — Document Split

**Prompt:** "put the config contract in CONFIG.md and the api contracts and interfaces in INTERFACES.md"

**Context:** PLAN became too dense with inline schemas and interfaces.

**Changes:**
- Created `docs/CONFIG.md` — metrics schema, experiment.json, hardware.json, .env
- Created `docs/INTERFACES.md` — BenchmarkSDK, InferenceProvider, InferenceRunner
- Updated `docs/PLAN.md` — replaced inline content with references to new files

---

## Entry 8 — TODO Creation

**Prompt:** "Yes" (to creating TODO.md)

**Context:** All docs ready. Need task tracking.

**Decision:** Created `docs/TODO.md` with 9 phases, 38 tasks, status tracking, Definition of Done per task.

---

## Entry 9 — Cautions and POC Steps

**Prompt:** "The steps lack cuation. can you explain in what way?"

**Context:** Tasks had no warnings about risks or pitfalls.

**Decision:** Explained: tasks lack cautions (OOM risk, hanging, mocking needs), dependency ordering, AirLLM complexity, no dry-run, implicit model downloads, gated models.

**Prompt:** "any other longer term issues you see?"

**Decision:** Identified: TDD violated (tests after implementation), no dependency graph, AirLLM weighted same as simple tasks, provider API incompatibilities, no validation step, no cleanup, no gated model handling.

**Prompt:** "Add the steps. no need for cleanup and to change the provider api. The provider api is a facade (no need to mention, just so you know)"

**Changes:**
- Moved tests alongside each phase (TDD compliance)
- Added `Depends` column for task ordering
- Added cautions (⚠️) to risky tasks
- Split AirLLM runner into 2 tasks (loading + generation)
- Added Phase 7: Pre-Benchmark (gated models, pre-download, hardware, validation)
- Updated task count to 43

---

## Entry 10 — Runner Cautions and POC Steps

**Prompt:** "No need to mention that airLLM is the most complex runner. Each runner should be treated with caution. Also, add poc module building for each step"

**Context:** AirLLM was singled out as "most complex." All runners should get equal caution. POC steps needed per phase.

**Changes:**
- Removed AirLLM-specific "most complex" caution
- Added cautions to all three runners (GPU: OOM/provider, CPU: OOM/hang, AirLLM: paged inference/150-line split)
- Added POC steps per phase:
  - Phase 4: POC minimal metrics + visualization pipeline
  - Phase 5: POC minimal runner pipeline
  - Phase 6: POC CLI → SDK smoke test
  - Phase 7: POC config + provider validation
  - Phase 8: POC full benchmark pipeline
- Updated task count to 49

---

## Entry 11 — Integration Plan

**Prompt:** "Please add an actual integration plan, instead of YOLO"

**Context:** POC steps exist but no formal integration strategy.

**Decision:** Added Integration Plan section to TODO.md with:
- 7 integration stages (I1–I7)
- Contract verification table (5 contracts)
- Mock vs Real progression table
- 6 integration checkpoints (CP1–CP6)
- Failure protocol (isolate → revert → fix → verify → advance)

**Prompt:** "I see that I7 integrates everything all at once"

**Context:** I7 was a "big bang" integration — all mocked to all real in one step.

**Changes:** Split I7 into 8 incremental stages (I7–I14):
- I7: Real Ollama + small model (metrics mocked)
- I8: Real Ollama + small model + real metrics
- I9: Real GPU runner + small model
- I10: Real CPU runner + small model
- I11: Real AirLLM runner + small model
- I12: All three runners + small model
- I13: Real CLI + SDK + small model
- I14: Full benchmark (large model)

**Prompt:** "where is transformers?"

**Context:** Transformers is default `cpu_baseline_provider` but not in integration stages.

**Changes:** Added Transformers integration:
- I8: Real Transformers provider + small model
- I11: Real CPU runner (Transformers) + real metrics
- Updated Mock vs Real table
- Updated checkpoints to CP1–CP12 with Transformers commands
- Renumbered stages to I7–I15

---

## Entry 12 — CLAUDE.md and Prompt Log

**Prompt:** "fit the claude.md to the project and add everything to the prompt log"

**Context:** CLAUDE.md was generic template. Needed project-specific rules. Prompt log needed.

**Changes:**
- Rewrote `CLAUDE.md` to reference this project's actual structure, docs, package name, architecture
- Added project context, mandatory documents table, package layout, providers layer description
- Updated all references from generic `src/<pkg>/` to `src/airllm_benchmark/`
- Added integration checkpoints to final checklist
- Created `docs/PROMPT_LOG.md` with full session history

---

## Entry 13 — Phase 1: Project Scaffolding

**Prompt:** "According to PRD, plan, prd, and todo, what do you think will be the best first step?"

**Context:** All mandatory documents complete. No source code exists. User wants to begin implementation.

**Decision:** Identified Phase 1 (Project Scaffolding) as the clear first step — nothing else can start without the foundation.

**Prompt:** "Start with the project scaffolding. Remember to listen to interfaces.md"

**Changes:**
- Created full directory structure per PLAN C4 (src/airllm_benchmark/{sdk, providers, services, shared}, tests/{unit, integration}, config, results, assets, notebooks)
- Updated `pyproject.toml` with all dependencies (airllm, ollama, psutil, matplotlib, pandas, pytest, ruff)
- Created `.env-example` with `HF_TOKEN` placeholder
- Created all `__init__.py` files with docstrings
- Implemented `constants.py` with `BenchmarkMode`, `RunStatus`, `QuantizationLevel` (StrEnum per INTERFACES.md mode/status values)
- Implemented `shared/version.py` (version `1.00`)
- `uv sync`: 83 packages resolved, all installed
- `ruff check src/`: 0 violations
- Package import verified: `__version__ = "1.00"`, all enums importable
- Updated `docs/TODO.md` — Phase 1 marked ✅ Done

**Prompt:** "commit and add to the prompt log. no phase 2"

**Changes:**
- Committed to git: `feat: Phase 1 — project scaffolding` (f40f8bd)
- Updated prompt log with this entry

---

## Summary of Documents

| Document | Status | Purpose |
|----------|--------|---------|
| `docs/PRD.md` | Complete | Requirements, goals, experiment design |
| `docs/PLAN.md` | Complete | C4 architecture, ADRs, data flow |
| `docs/CONFIG.md` | Complete | Config schemas, metrics record |
| `docs/INTERFACES.md` | Complete | SDK API, provider/runner contracts |
| `docs/TODO.md` | Complete | Tasks, integration plan, checkpoints |
| `docs/PROMPT_LOG.md` | Complete | Session history, decisions |
| `CLAUDE.md` | Updated | Project-specific rules |
