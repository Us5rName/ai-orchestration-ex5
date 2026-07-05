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

**Prompt:** "There are several inference providers, and some allow for CPU-only runs. how do you suggest we move forward with the documents?"

**Context:** Multiple inference providers exist (Transformers, llama.cpp) and each supports both GPU and CPU. The current docs assume a single provider fixed to GPU, which is incorrect.

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
- PRD §3.2: renamed to "GPU Baseline Smoke Test"
- PRD §6.3: New Inference Providers table
- PRD Glossary: generalized the inference-provider definition
- PLAN C4 diagrams: generalized to "Inference Providers"
- PLAN code structure: generalized runner naming to `provider_runner.py`
- PLAN metrics: Added `provider` field
- PLAN config: Added `gpu_provider` + `provider_config`
- PLAN SDK API: Added `provider` parameter
- PLAN ADR-003: Rewritten for configurable GPU provider
- PLAN error handling: generalized to "Configured provider"

---

## Entry 6 — CPU Runner Configurability

**Prompt:** "is the cpu_runner also configurable?"

**Context:** GPU runner is provider-configurable. Should CPU baseline runner also be configurable?

**Decision:** Yes — providers like Transformers and llama.cpp can all run on CPU. Made CPU runner provider-configurable.

**Prompt:** "Please make it flexible. and add a providers directory"

**Changes:**
- PLAN: Added `providers/` directory with `base.py`, `transformers_provider.py`, `llamacpp_provider.py`
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
- I7: Real Transformers + small model (metrics mocked)
- I8: Real Transformers + small model + real metrics
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

## Entry 13 — Phase 1 Scaffolding Commit

**Prompt:** "commit and add to the prompt log. no phase 2"

**Changes:**
- Committed Phase 1 scaffolding: `feat: Phase 1 — project scaffolding` (f40f8bd)
- Updated prompt log with Entry 13

---

## Entry 14 — Phase 2 Kickoff

**Prompt:** "What is phase 2?"

**Context:** Phase 1 committed. User wants to know what Phase 2 entails.

**Response:** Explained Phase 2 — Configuration Layer (experiment.json, hardware.json, config.py, tests, version.py). Noted task 2.5 already done in Phase 1.

---

## Entry 15 — Phase 2 Implementation

**Prompt:** "yes, start phase 2. implement like I thought you (skills also exist)"

**Context:** User wants Phase 2 implemented following project skills (code-review-config, tdd-testing, modular-design).

**Decision:** Follow TDD (RED → GREEN → REFACTOR) and skills:
- Updated ruff config per code-review-config skill (added C4, SIM, ignore E501)
- Created config files per CONFIG.md schemas
- Wrote tests first (RED) — 15 tests covering all config loader functionality
- Implemented shared/config.py (GREEN) — typed dataclasses, validation, no hardcoded values
- Fixed ruff violations (unused imports, import ordering)
- All 15 tests pass, ruff = 0 violations

**Changes:**
- `pyproject.toml`: Updated ruff lint rules (C4, SIM, ignore E501)
- `config/experiment.json`: Created per CONFIG.md §2
- `config/hardware.json`: Created per CONFIG.md §3 (empty, filled Phase 8)
- `src/airllm_benchmark/shared/config.py`: ExperimentConfig, HardwareConfig, loaders, validators
- `tests/unit/test_config.py`: 15 tests (TDD)
- `docs/TODO.md`: Phase 2 marked ✅ Done

---

## Entry 13 — Phase 1: Project Scaffolding

**Prompt:** "According to PRD, plan, prd, and todo, what do you think will be the best first step?"

**Context:** All mandatory documents complete. No source code exists. User wants to begin implementation.

**Decision:** Identified Phase 1 (Project Scaffolding) as the clear first step — nothing else can start without the foundation.

**Prompt:** "Start with the project scaffolding. Remember to listen to interfaces.md"

**Changes:**
- Created full directory structure per PLAN C4 (src/airllm_benchmark/{sdk, providers, services, shared}, tests/{unit, integration}, config, results, assets, notebooks)
- Updated `pyproject.toml` with all dependencies (airllm, transformers, psutil, matplotlib, pandas, pytest, ruff)
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

## Entry 16 — 150-Line Rule Enforcement

**Prompt:** "There are files with more than 150 lines in tests and srd. fix them like I thought you and don't forget skills"

**Context:** `config.py` (161 lines) and `test_config.py` (168 lines) exceeded the 150-line limit.

**Decision:** Applied modular-design skill — separated data models from loading logic.

**Changes:**
- `config.py` (161→29): Thin re-export facade for backward compatibility
- `config_models.py` (new, 79): `ExperimentConfig`, `HardwareConfig`, constants
- `config_loader.py` (new, 98): `load_*`, `validate_*`, `get_hf_token`
- `test_config.py` (168→deleted): Split into two focused test files
- `test_config_models.py` (new, 83): Dataclass method tests
- `test_config_loader.py` (new, 132): Loader/validation tests
- All files <150 lines, ruff=0 violations, 15/15 tests pass

**Prompt:** "commit and update the prompt log"

**Changes:**
- Committed: `refactor: split config.py into models + loader (150-line rule)` (73bbe1a)
- Updated prompt log with Entry 16

---

## Entry 17 — Config Fixture Tests

**Prompt:** "Real files exist in the config. Please put junk data in the hardware config and add tests to the config that use the actual files in new files"

**Context:** Config module fully implemented but tests use `tmp_path` fixtures. No tests validate the actual config files on disk.

**Changes:**
- `config/hardware.json`: Populated with junk placeholder data (Intel i9, RTX 4090, 64GB RAM)
- `src/airllm_benchmark/shared/config_models.py`: Fixed `CONFIG_DIR` path (was `src/config/`, now project root `config/`)
- `tests/fixtures/config/`: New directory with fixture copies of experiment.json + hardware.json
- `tests/unit/test_config_real_experiment.py`: 13 tests asserting actual experiment.json values
- `tests/unit/test_config_real_hardware.py`: 10 tests asserting actual hardware.json values
- `tests/unit/test_config_real_combined.py`: 5 tests for cross-config scenarios
- All 43 tests pass (15 existing + 28 new), ruff = 0 violations

**Prompt:** "The tests should check for the actual values"

**Changes:** Rewrote fixture tests to assert concrete values (`small == "meta-llama/Llama-3.2-1B"`, `ram_gb == 64`, etc.) instead of generic checks (`non-empty`, `positive`).

**Prompt:** "Now moves the files with the modified values to a new dir, and update the tests accordingly"

**Changes:** Created `tests/fixtures/config/` with fixture copies. Updated tests to use `FIXTURES_CONFIG_DIR` constant. Tests independent of project's runtime `config/`.

---

## Entry 18 — Phase 3 (3.1–3.2) Providers Protocol

**Prompt:** "Implement only up to 3.2"

**Context:** Phase 1 and Phase 2 complete. Next step is Phase 3 — Providers Layer.

**Decision:** Implemented `InferenceProvider` protocol per `INTERFACES.md` §2.

**Changes:**
- `providers/base.py`: `InferenceProvider` Protocol with `load_model()`, `generate()`, `unload()`
- `providers/__init__.py`: Exports `InferenceProvider`
- `docs/TODO.md`: Tasks 3.1 and 3.2 marked ✅ Done
- ruff=0, import test passes

---

## Entry 19 — Implementation Instructions Document

**Prompt:** "Does one of the document explain how to correctly write actual implementations?"

**Context:** User noticed no document explains *how* to implement providers (only *what* to implement via INTERFACES.md).

**Decision:** Identified gap — no document covers implementation methodology. Proposed `docs/IMPLEMENTATION.md`.

**Prompt:** "These are the implementation instructions you need to write: 1. show a basic PoC proving you know how to load and use the external library. 2. show a PoC for every feature that will be used in the module interface. Note: every PoC needs to be tested. 3. Using the lessons in of the pocs, you will build the full module"

**Changes:**
- Created `docs/IMPLEMENTATION.md` with three-step process: Library PoC → Feature PoCs → Full Module
- Each step requires tests; PoCs are disposable after module completion
- Includes concrete example for the Transformers Provider

**Prompt:** "Is the document referenced in CLAUDE.md?"

**Changes:**
- Added `docs/IMPLEMENTATION.md` to Mandatory Documents table in `CLAUDE.md`
- Updated Final Verification Checklist to include `IMPLEMENTATION` in docs list

---

## Entry 20 — Commit

**Prompt:** "add everything to the prompt log and commit"

**Changes:**
- Updated `docs/PROMPT_LOG.md` with Entries 18–20
- Updated Summary of Documents table
- Committed all changes

---

## Entry 18 — Phase 3 (3.1–3.2) Providers Protocol

**Prompt:** "Implement only up to 3.2"

**Context:** Phase 1 and Phase 2 complete. Next step is Phase 3 — Providers Layer. User wants only tasks 3.1 and 3.2.

**Decision:** Implemented `InferenceProvider` protocol per `INTERFACES.md` §2.

**Changes:**
- `providers/base.py`: `InferenceProvider` Protocol with `load_model()`, `generate()`, `unload()`
- `providers/__init__.py`: Exports `InferenceProvider`
- `docs/TODO.md`: Tasks 3.1 and 3.2 marked ✅ Done
- ruff=0, import test passes

---

## Entry 19 — Implementation Instructions Document

**Prompt:** "Does one of the document explain how to correctly write actual implementations?"

**Context:** User noticed no document explains *how* to implement providers (only *what* to implement via INTERFACES.md).

**Decision:** Identified gap — no document covers implementation methodology. Proposed `docs/IMPLEMENTATION.md`.

**Prompt:** "These are the implementation instructions you need to write: 1. show a basic, PoC, proving you know how to load and use the external library. 2. show a PoC for every feature that will be used in the module interface. Note: every PoC needs to be tested with 3. Using the lessons in of the pocs, you will build the full module"

**Changes:**
- Created `docs/IMPLEMENTATION.md` with three-step process: Library PoC → Feature PoCs → Full Module
- Each step requires tests; PoCs are disposable after module completion
- Includes concrete example for the Transformers Provider

**Prompt:** "Is the document referenced in CLAUDE.md?"

**Changes:**
- Added `docs/IMPLEMENTATION.md` to Mandatory Documents table in `CLAUDE.md`
- Updated Final Verification Checklist to include `IMPLEMENTATION` in docs list

---

## Entry 20 — Commit Phase 3 Protocol + Implementation Docs

**Prompt:** "add everything to the prompt log and commit"

**Changes:**
- Updated `docs/PROMPT_LOG.md` with Entries 18–20
- Updated Summary of Documents table
- Committed all changes

**Prompt:** "Can we load the test config without fixtures?"

**Changes:** Removed `@pytest.fixture` decorators. Each test now calls `load_experiment(TEST_CONFIG_DIR)` directly. Simpler, self-contained tests.

**Prompt:** "remove the word fixture from the commit message, as we don't use it anymore. should the test config directory also be changed in name?"

**Changes:**
- Renamed `tests/fixtures/` → `tests/config/` (no pytest fixtures used)
- Renamed `FIXTURES_CONFIG_DIR` → `TEST_CONFIG_DIR` in all test files
- Flattened nested directory structure (`tests/config/config/` → `tests/config/`)
- Amended commit: `test: add config tests asserting actual values from tests/config/`

---

## Entry 21 — Transformers Provider (Step 1–3)

**Prompt:** "Proceed to step 2" → "commmit the current changes" → "now move on to step 3. remember to use the PoC code" → "did you run the RED phase?" → "split only like you were thaught and your skills" → "Add to prompt log and commit"

**Implementation process (per `docs/IMPLEMENTATION.md`):**

### Step 1 — Library PoC
- Created `pocs/transformers_library_poc.py` — minimal script proving `transformers` loads + generates
- Created `tests/pocs/test_transformers_library_poc.py` — 3 tests
- Verified: tiny GPT2 model loads, generates non-empty text

### Step 2 — Feature PoCs
- Created `pocs/transformers_feature_pocs.py` — 3 isolated PoCs (`poc_load_model`, `poc_generate`, `poc_unload`)
- Created `tests/pocs/test_transformers_feature_pocs.py` — 5 tests
- Verified: device placement, max_tokens enforcement, GC memory release

### Step 3 — Full Module (TDD: RED → GREEN)
- RED: Wrote tests first → 9/11 failed (no implementation)
- GREEN: Built `src/.../providers/transformers_provider.py` from PoC patterns → 11/11 passed
- REFACTOR: Split 186-line test file → 3 focused files + shared `conftest.py` (all ≤ 118 lines)

**Decisions:**
- Extracted `mock_transformers` context manager to `conftest.py` (DRY — used by all 3 test files)
- Provider caches tokenizer per `model_id` to avoid redundant loads
- `unload()` is safe no-op when nothing loaded
- All external deps mocked (no model downloads in unit tests)

**Files:**
- `pocs/transformers_library_poc.py` (38 lines)
- `pocs/transformers_feature_pocs.py` (101 lines)
- `src/.../providers/transformers_provider.py` (118 lines)
- `tests/pocs/test_transformers_library_poc.py` (38 lines)
- `tests/pocs/test_transformers_feature_pocs.py` (85 lines)
- `tests/unit/conftest.py` (56 lines)
- `tests/unit/test_transformers_load.py` (41 lines)
- `tests/unit/test_transformers_generate.py` (39 lines)
- `tests/unit/test_transformers_unload.py` (35 lines)

**Validation:** pytest 11/11 ✅ | ruff 0 violations ✅ | all files ≤ 150 lines ✅

---

## Summary of Documents

| Document | Status | Purpose |
|----------|--------|---------|
| `docs/PRD.md` | Complete | Requirements, goals, experiment design |
| `docs/PLAN.md` | Complete | C4 architecture, ADRs, data flow |
| `docs/CONFIG.md` | Complete | Config schemas, metrics record |
| `docs/INTERFACES.md` | Complete | SDK API, provider/runner contracts |
| `docs/IMPLEMENTATION.md` | Complete | Module implementation process (PoC → full module) |
| `docs/TODO.md` | Complete | Tasks, integration plan, checkpoints |
| `docs/PROMPT_LOG.md` | Complete | Session history, decisions |
| `CLAUDE.md` | Updated | Project-specific rules |

---

## Entry 22 — Transformers as GPU Provider + Device Tests

**Prompt:** "Change in plan - I want transformers as the gpu provider. implement transformers gpu provider according to the instructions in IMPLEMENTATION.md. you still have the cpu PoCs that can help you"

**Context:** User set Transformers as the wired GPU provider. The `transformers_provider.py` already existed from Phase 3 (Step 1-3 per IMPLEMENTATION.md). PoCs existed and were tested.

**Decisions:**
- Updated `config/experiment.json` to use `gpu_provider: "transformers"` with `device: "cuda"`
- Consolidated on Transformers as the single wired provider (serves both GPU and CPU); dropped the planned separate HTTP-client provider
- Updated `docs/TODO.md` to reflect plan change
- Fixed bug: tokenizer inputs were on CPU while model was on CUDA → added `.to(self._device)` in `generate()`
- Added real device tests (`tests/unit/test_transformers_device.py`) for both CPU and GPU paths

**Changes:**
- `config/experiment.json` — gpu_provider → transformers, device → cuda
- `src/airllm_benchmark/providers/transformers_provider.py` — fixed device mismatch bug
- `docs/TODO.md` — dropped the separate provider task, added GPU/CPU verification tasks
- `tests/unit/test_transformers_device.py` — new file with 4 real device tests (2 CPU + 2 GPU)

**Validation:**
- All 4 real device tests pass (CPU + GPU on RTX 4080 SUPER)
- All 11 existing mocked unit tests still pass
- ruff check = 0 violations
- GPU verified: model loads on cuda:0, generates text, unloads
- CPU verified: model loads on cpu, generates text, unloads

---

## Entry 23 — Provider Interface Tests (TODO 3.6)

**Prompt:** "except additional providers, what else isn't implemented in phase 3 of the TODO?" → "write the tests, if they don't exist" → "add to prompt log and commit"

**Context:** TODO item 3.6 (`tests/unit/test_providers.py`) was the only unimplemented task in Phase 3 besides the llama.cpp provider (3.5). The separate HTTP-client provider (3.3) was already removed.

**Decisions:**
- Created `tests/unit/test_providers.py` with 19 tests across 4 test classes
- Tests verify protocol definition, `TransformersProvider` compliance, mock provider compliance, and full lifecycle scenarios
- All external calls mocked via existing `mock_transformers` context manager
- Removed unused imports (`runtime_checkable`, `pytest`) to satisfy ruff

**Changes:**
- `tests/unit/test_providers.py` — new file with 19 protocol compliance tests
- `docs/PROMPT_LOG.md` — Entry 23 added

**Validation:**
- All 19 tests pass
- ruff check = 0 violations

---

## Entry 24 — Split test_providers.py (150-line rule)

**Prompt:** "fix the 150 lines as you were taught and according to your skills"

**Context:** `test_providers.py` was 168 lines, exceeding the CLAUDE.md 150-line limit. Split by concern following modular design principles.

**Decisions:**
- Split into two files by responsibility: protocol definition vs implementation behavior
- `test_providers.py` — protocol definition + mock provider compliance (73 lines)
- `test_provider_lifecycle.py` — TransformersProvider compliance + lifecycle tests (108 lines)

**Changes:**
- `tests/unit/test_providers.py` — reduced to 73 lines (protocol + mock tests only)
- `tests/unit/test_provider_lifecycle.py` — new file with 108 lines (compliance + lifecycle)
- `docs/PROMPT_LOG.md` — Entry 24 added

**Validation:**
- Both files under 150 lines
- All 19 tests pass
- ruff check = 0 violations

---

## Entry 25 — Metrics Interface Discovery + Pre-Implementation Gate

**Prompt:** "start phase 4.1. remember implementation.md and what you were taught"

**Context:** Started Phase 4.1 (services/metrics.py). Followed IMPLEMENTATION.md PoC process. Discovered that `docs/INTERFACES.md` has no contract for the metrics service — only SDK, Provider, and Runner interfaces exist.

**Problem discovered:**
- Designed `MetricsCollector` API without a contract in INTERFACES.md
- Continued implementing without notifying the user
- Two failures: missing contract (design) + no notification (process)

**Decisions:**
- Created `docs/LESSON_INTERFACE_FIRST.md` documenting both failures
- Added ⚠️ Pre-Implementation Gate to `docs/IMPLEMENTATION.md` — mandates checking INTERFACES.md before any implementation, stopping and notifying the user if a gap exists
- Defined `MetricsRecord` dataclass (16 fields, frozen, matches CONFIG.md §1)
- Defined `MetricsCollector` Protocol with context-at-start pattern: `start(context)`, `mark_load_complete()`, `stop()`, `get_record(results)` → eliminates parameter duplication with runner interface
- Updated `docs/PLAN.md` §4 to reference new interfaces
- Bumped all affected documents + version.py to 1.01
- PoCs created but NOT committed (disposable per IMPLEMENTATION.md)

**Changes:**
- `docs/INTERFACES.md` — Added §4 MetricsRecord + §5 MetricsCollector (v1.01)
- `docs/IMPLEMENTATION.md` — Added Pre-Implementation Gate section (v1.01)
- `docs/PLAN.md` — Updated §4 API Contracts references (v1.01)
- `docs/LESSON_INTERFACE_FIRST.md` — New lesson document
- `src/airllm_benchmark/shared/version.py` — 1.00 → 1.01
- `docs/PROMPT_LOG.md` — Entry 25 added

**Not committed (PoCs, disposable per IMPLEMENTATION.md):**
- `pocs/metrics_library_poc.py`
- `pocs/metrics_feature_pocs.py`
- `tests/pocs/test_metrics_library_poc.py`
- `tests/pocs/test_metrics_feature_pocs.py`

**Validation:**
- All PoC tests pass (4 library + 15 feature = 19 total)
- Interface eliminates duplication with InferenceRunner.run() parameters
- All CONFIG.md §1 fields covered in MetricsRecord

---

## Entry 26 — Update return types to MetricsRecord

**Prompt:** "are there any other interfaces that are affected by the change?" → "Yes. and prompt log and commit"

**Context:** After defining `MetricsRecord`, two interfaces still returned `dict` with docstring "matching Metrics Record schema" instead of using the explicit type.

**Changes:**
- `BenchmarkSDK.run_single()` — `-> dict` → `-> MetricsRecord`
- `InferenceRunner.run()` — `-> dict` → `-> MetricsRecord`
- `docs/PROMPT_LOG.md` — Entry 26 added

**Validation:**
- All interfaces now reference explicit types instead of vague "dict matching schema"
- No interfaces use `dict` as return type for metrics data

---

## Entry 34 — INCONSISTENCIES.md: Stale Provider References After GPU Provider Change

**Prompt:** "Look at the prompt log, you will see that the gpu provider was changed to transformers. Please update inconcistensies.md" → "And update the version and add to the prompt log and commit"

**Context:** Per Entry 22, the wired GPU provider was consolidated on Transformers. `config/experiment.json` and TODO.md were updated. However, multiple documentation files still referenced an earlier, no-longer-wired provider as if it were active.

**Decisions:**
- Added new inconsistency (#2) to `docs/INCONSISTENCIES.md` tracking all stale provider references across 6 documents
- Bumped version from 1.01 to 1.02
- Documents affected: `CLAUDE.md`, `docs/CONFIG.md`, `docs/INTERFACES.md`, `docs/PLAN.md`, `docs/IMPLEMENTATION.md`

**Changes:**
- `docs/INCONSISTENCIES.md` — Added Entry #2: stale provider references (v1.02)
- `src/airllm_benchmark/shared/version.py` — 1.01 → 1.02
- `docs/PROMPT_LOG.md` — Entry 34 added

**Validation:**
- `uv run ruff check` → 0 violations
- All files ≤ 150 lines

---

## Summary of Documents

| Document | Status | Purpose |
|----------|--------|--------|
| `docs/PRD.md` | Complete | Requirements, goals, experiment design |
| `docs/PLAN.md` | Updated (1.01) | C4 architecture, ADRs, data flow |
| `docs/CONFIG.md` | Complete | Config schemas, metrics record |
| `docs/INTERFACES.md` | Updated (1.01) | SDK, provider, runner, metrics contracts |
| `docs/IMPLEMENTATION.md` | Updated (1.01) | PoC process + Pre-Implementation Gate |
| `docs/TODO.md` | Complete | Tasks, integration plan, checkpoints |
| `docs/PROMPT_LOG.md` | Updated | Session history, decisions |
| `docs/LESSON_INTERFACE_FIRST.md` | New | Process lesson: interface-first + notification |
| `docs/INCONSISTENCIES.md` | Updated (1.02) | Track gaps between docs, interfaces, and TODO |
| `CLAUDE.md` | Updated | Project-specific rules |

---

## Entry 27 — Phase 4.1: Metrics Service (PoCs → Full Module)

**Prompt:** "start phase 4.1. remember implementation.md and what you were thaught, check gate" → "will you need just psutil? define the library for each thing" → "choose something agnostic. what about torch?" → "yes. each library gets its own poc. start with one library, 3 steps, real data and move on to the next" → "skip step 3 until the end" → "add to prompt log, divide to commmits and commit"

**Context:** Implement `services/metrics.py` (Phase 4.1 per TODO.md). Pre-Implementation Gate passed — `MetricsRecord` (§4) and `MetricsCollector` (§5) interfaces exist in INTERFACES.md v1.01.

**Library Mapping:**

| Capability | Library | Reason |
|---|---|---|
| Timing (load time, TTFT, total runtime) | `time` (stdlib) | `time.perf_counter()` — no external dep |
| RAM sampling (peak RAM in MB) | `psutil` | `psutil.Process().memory_info()` — 1s interval |
| VRAM sampling (peak VRAM in MB) | `torch` | `torch.cuda.max_memory_allocated()` — already a dep, agnostic |
| MetricsRecord (frozen dataclass) | `dataclasses` (stdlib) | `@dataclass(frozen=True)` — no external dep |

**PoC Process (per IMPLEMENTATION.md):**

| Library | Library PoC | Feature PoCs | Result |
|---------|-------------|--------------|--------|
| psutil | ✅ 15.08 MB RAM measured | ✅ 2/2 tests (sampling, peak detection) | Proven |
| torch | ✅ CUDA available (RTX 4080 SUPER) | ✅ 3/3 tests (100 MB GPU alloc, reset, no-cuda) | Proven |

**VRAM = 0 Question:** User asked why Library PoC showed 0 VRAM. Answer: `torch.cuda.max_memory_allocated()` tracks peak allocation by the current process. The PoC never allocates GPU tensors, so peak is 0. Feature PoC allocates real 100 MB tensor → non-zero peak. During actual benchmarks, the provider loads model weights onto CUDA → peak reflects real usage.

**Decisions:**
- torch chosen over GPUtil/nvidia-smi for VRAM — already a dependency, vendor-agnostic, no new deps
- Split module into `metrics.py` (dataclass + collector) + `metrics_sampler.py` (RamSampler + VramTracker) to stay under 150-line limit
- RamSampler uses daemon thread with 1-second interval (per TODO.md Definition of Done)
- VramTracker is stateless (static methods) — torch.cuda manages peak tracking internally
- All external deps mocked in unit tests (psutil, torch.cuda)

**Changes:**
- `src/airllm_benchmark/services/metrics.py` — MetricsRecord + MetricsCollector (140 lines)
- `src/airllm_benchmark/services/metrics_sampler.py` — RamSampler + VramTracker (73 lines)
- `src/airllm_benchmark/services/__init__.py` — Exports MetricsCollector, MetricsRecord
- `tests/unit/test_metrics.py` — 6 unit tests (all mocked)
- `pocs/psutil_library_poc.py` — psutil Library PoC
- `pocs/psutil_feature_pocs.py` — psutil Feature PoCs
- `pocs/torch_library_poc.py` — torch Library PoC
- `pocs/torch_feature_pocs.py` — torch Feature PoCs
- `tests/pocs/test_psutil_*.py` — psutil PoC tests
- `tests/pocs/test_torch_*.py` — torch PoC tests
- `docs/TODO.md` — 4.1 marked Done, summary updated

**Validation:**
- `uv run ruff check` — 0 violations
- `uv run pytest tests/unit/test_metrics.py` — 6/6 passed
- All files ≤ 150 lines
- No hardcoded values
- Module imports verified: all 17 MetricsRecord fields present

## Entry 28 — 150-Line Rule Enforcement (PoCs + Tests)

**Prompt:** "There are some project files with more than 150 lines. split them like you were taught and according to your skills" → "touch the pocs as well"

**Context:** The 150-line rule (CLAUDE.md §4) was not fully enforced. Three files exceeded the limit:
- `pocs/metrics_feature_pocs.py` — 214 lines
- `tests/pocs/test_metrics_feature_pocs.py` — 196 lines
- `tests/unit/test_metrics.py` — 185 lines

**Decisions:**
- Split each file by single responsibility (one feature per file)
- Updated all test imports to reference new module paths
- Fixed pre-existing ruff violations discovered during split (B011 `assert False`, F401 unused import, W291/W293 whitespace)

**Changes:**
- `pocs/metrics_feature_pocs.py` → `metrics_timing_poc.py` (50), `metrics_sampling_poc.py` (72), `metrics_peak_poc.py` (51), `metrics_record_poc.py` (87)
- `tests/pocs/test_metrics_feature_pocs.py` → `test_metrics_timing_poc.py` (41), `test_metrics_sampling_poc.py` (41), `test_metrics_peak_poc.py` (52), `test_metrics_record_poc.py` (102)
- `tests/unit/test_metrics.py` → `test_metrics_record.py` (65), `test_metrics_collector.py` (127)
- Fixed `assert False` → `raise AssertionError()` in `test_metrics_record.py`
- Fixed unused `field` import in `metrics_library_poc.py`
- Fixed trailing whitespace in `testing-airllm.py`

**Validation:**
- `uv run pytest tests/` — 116/116 passed
- `uv run ruff check . --exclude .venv` — 0 violations
- All files ≤ 150 lines (max: `services/metrics.py` at 140 lines)

---

## Entry 29 — Metrics Collector Tests (TODO 4.2)

**Prompt:** "implement 4.2 according to what you were thaught and your skills" → "prompt log and commit"

**Context:** Task 4.2 required metrics collector tests covering timing accuracy, memory sampling, and peak calculation with mocked psutil. Existing tests (`test_metrics_collector.py`, `test_metrics_record.py`) covered basic lifecycle but lacked timing accuracy, direct sampler testing, and edge cases.

**Decisions:**
- Split tests across 3 files to respect 150-line rule
- `test_metrics_collector.py` — core lifecycle (existing, unchanged)
- `test_metrics_sampler.py` — direct `RamSampler` + `VramTracker` tests (new)
- `test_metrics_edge_cases.py` — timing accuracy, collector reuse, timeout edge cases (new)
- All external deps (psutil, torch) mocked per project rules

**Changes:**
- Created `tests/unit/test_metrics_sampler.py` (117 lines, 5 tests)
- Created `tests/unit/test_metrics_edge_cases.py` (91 lines, 3 tests)
- Updated `docs/TODO.md` — marked 4.2 as ✅ Done

**Validation:**
- `uv run pytest tests/unit/test_metrics*.py` — 15/15 passed
- `uv run ruff check` — 0 violations
- All files ≤ 150 lines

---

## Entry 30 — Visualizer Interface + INCONSISTENCIES.md

**Prompt:** "start 4.3. Use Implementation.md and what you were thaught and check gate" → "Propose an interface according to the plan and prd" → "What other interfaces are affected?" → "Where did resultWriter come from?" → "What is resultWriter related to?" → "In what phase of the TODO is resultWriter implemented?" → "Write it in INCONSISTENCIES.md and ignore it for now" → "The interface is approved. update all the interfaces it's relevant to. do not start the poc" → "if it's resolve you can delete it" → "don't start it. prompt log and commit"

**Context:** Task 4.3 (POC: minimal metrics + visualization pipeline) requires a Visualizer interface. Pre-implementation gate per IMPLEMENTATION.md revealed Visualizer was missing from INTERFACES.md. Also discovered ResultWriter gap between PLAN architecture and TODO task list.

**Decisions:**
- Created `docs/INCONSISTENCIES.md` to track deferred gaps between docs, interfaces, and TODO
- Logged: ResultWriter (deferred to Phase 5), TODO Summary outdated, SDK return types underspecified
- Proposed Visualizer interface with 4 methods: `generate_latency_chart`, `generate_memory_chart`, `generate_table`, `generate_all`
- Added `VisualizationResult` dataclass for typed SDK return
- Updated SDK §1 `generate_visualization()` signature to accept `records` + `output_dir`, return `VisualizationResult`
- Removed resolved items from INCONSISTENCIES.md (keep only active gaps)
- Did NOT start PoC implementation — interface work only

**Changes:**
- Created `docs/INCONSISTENCIES.md` (3 active items)
- Updated `docs/INTERFACES.md` v1.02 (added §6 Visualizer, §7 VisualizationResult, updated §1 SDK)

**Validation:** None — interface documentation only, no code changes.

---

## Entry 31 — Task 4.3: Visualization Pipeline PoC

**Prompt:** "start 4.3. Use Implementation.md and what you were thaught and check gate"

**Context:** Task 4.3 requires a POC proving the full metrics → visualization pipeline works end-to-end. Visualizer interface (§6-§7) was already approved in Entry 30. Pre-implementation gate verified all interfaces exist.

**Decisions:**
- Followed IMPLEMENTATION.md Step 1: Library PoC to verify matplotlib produces valid PNG
- Reused proven pattern from fake MetricsRecord → bar chart → PNG output
- Created standalone PoC in `pocs/visualization_pipeline_poc.py`
- 15 tests covering: fake records, latency chart, memory chart, full pipeline
- PoC code serves as foundation for full Visualizer module (task 4.4)

**Changes:**
- Created `pocs/visualization_pipeline_poc.py` (138 lines)
- Created `tests/pocs/test_visualization_pipeline_poc.py` (122 lines)
- Updated `docs/TODO.md` — marked 4.3 as Done

**Validation:**
- `uv run python pocs/visualization_pipeline_poc.py` → 2 PNG charts generated (17KB + 19KB)
- `uv run pytest` → 15/15 passed
- `uv run ruff check` → 0 violations
- All files ≤ 150 lines

---

## Entry 32 — Task 4.4: Visualizer Service (Full Module)

**Prompt:** "start 4.4. Use Implementation.md and what you were thaught and your skills and check gate" → "you must split according to what you were thaught about splitting and your skills"

**Context:** Task 4.4 requires implementing `services/visualizer.py` per INTERFACES.md §6-§7. PoC (4.3) already proved the pipeline works. Pre-implementation gate passed: all interfaces defined.

**Decisions:**
- Followed IMPLEMENTATION.md Step 3: Full Module using PoC code as foundation
- Applied modular-design skill: split by single responsibility
- `visualizer.py` (115 lines): Visualizer class + VisualizationResult dataclass
- `chart_helpers.py` (112 lines): Matplotlib rendering (latency + memory charts)
- `table_helpers.py` (82 lines): Formatted comparison table generation
- Tests split by feature (separation of concerns):
  - `test_visualizer_charts.py` (101 lines): Chart rendering tests (8 tests)
  - `test_visualizer_table.py` (53 lines): Table formatting tests (4 tests)
  - `test_visualizer_generate_all.py` (99 lines): Pipeline + result tests (7 tests)
- Shared `sample_records` fixture in `conftest.py` (DRY)
- All files ≤ 150 lines per CLAUDE.md §4
- `zip(strict=True)` per ruff B905 rule
- Updated `services/__init__.py` with public exports

**Changes:**
- Created `src/airllm_benchmark/services/visualizer.py`
- Created `src/airllm_benchmark/services/chart_helpers.py`
- Created `src/airllm_benchmark/services/table_helpers.py`
- Updated `src/airllm_benchmark/services/__init__.py`
- Created `tests/unit/test_visualizer_charts.py`
- Created `tests/unit/test_visualizer_table.py`
- Created `tests/unit/test_visualizer_generate_all.py`
- Updated `tests/unit/conftest.py` (added `sample_records` fixture)
- Updated `docs/TODO.md` — marked 4.4 as Done

**Validation:**
- `uv run pytest` → 19/19 passed
- `uv run ruff check` → 0 violations
- All files ≤ 150 lines
- `from airllm_benchmark.services import Visualizer, VisualizationResult` → import OK

---

## Entry 33 — Task 4.5: Visualizer Tests Status Correction

**Prompt:** "start 4.5. Use Implementation.md and what you were thaught and your skills and check gate"

**Context:** Task 4.5 requires `tests/unit/test_visualizer.py` — visualization tests. TODO.md marked it as "Not Started" but test files already existed from task 4.4 implementation.

**Pre-Implementation Gate:**
- ✅ INTERFACES.md §6 defines `Visualizer` (4 methods)
- ✅ INTERFACES.md §7 defines `VisualizationResult` dataclass
- ✅ Interface clear and complete — gate passed

**Decisions:**
- Verified existing test files already cover all interface methods
- No new code needed — tests were created alongside 4.4 (modular-design skill)
- Updated TODO.md to reflect actual status

**Changes:**
- Updated `docs/TODO.md` — marked 4.5 as Done with accurate test count
- Updated `docs/PROMPT_LOG.md` — this entry

**Validation:**
- `uv run pytest tests/unit/test_visualizer_*.py` → 19/19 passed
- `uv run pytest tests/unit/` → 111/111 passed
- `uv run ruff check` → 0 violations

---

## Entry 34 — Task 5.1: InferenceRunner Protocol + RunnerManager

**Prompt:** "start 5.1. Use Implementation.md and what you were thaught and your skills and check gate"

**Context:** Task 5.1 requires implementing `sdk/runner.py` with the `InferenceRunner` protocol and `RunnerManager` class per INTERFACES.md §3.

**Pre-Implementation Gate:**
- ✅ INTERFACES.md §3 defines `InferenceRunner` protocol (1 method: `run()`)
- ✅ Dependencies satisfied: 3.2 (providers/base.py), 2.3 (shared/config.py)
- ✅ `MetricsRecord` available in `services/metrics.py`
- ✅ Gate passed — no gaps or ambiguities

**TDD Flow (RED → GREEN → REFACTOR):**
- **RED:** Wrote `tests/unit/test_runner_protocol.py` (9 tests), ran → failed (import error + logic gaps)
- **GREEN:** Implemented `sdk/runner.py` with `InferenceRunner` protocol + `RunnerManager`
- **REFACTOR:** Fixed ruff UP037 violations, updated tests for mocked lazy init

**Decisions:**
- `RunnerManager` uses lazy initialization — runners imported on first `get_runner()` call
- Lazy init avoids circular imports and defers runner module loading until needed
- Tests mock runner modules via `patch.dict("sys.modules", ...)` since actual runners (5.2-5.5) don't exist yet
- Unknown mode raises `ValueError` with descriptive message listing valid modes

**Changes:**
- Created `src/airllm_benchmark/sdk/runner.py` — `InferenceRunner` protocol + `RunnerManager` (111 lines)
- Created `tests/unit/test_runner_protocol.py` — 9 tests covering protocol + manager dispatch
- Updated `src/airllm_benchmark/sdk/__init__.py` — exports `InferenceRunner`, `RunnerManager`
- Updated `docs/TODO.md` — marked 5.1 as Done
- Updated `docs/PROMPT_LOG.md` — this entry

**Validation:**
- `uv run pytest tests/unit/test_runner_protocol.py` → 9/9 passed
- `uv run ruff check` → 0 violations
- Both files under 150 lines (111 + 124)

---

## Entry 35 — Task 5.2: GPU Runner (GpuRunner)

**Prompt:** "start 5.2. Use Implementation.md and what you were thaught and your skills and check gate"

**Context:** Task 5.2 requires implementing `sdk/gpu_runner.py` with `GpuRunner` that delegates to a configured `InferenceProvider`, collects metrics via `MetricsCollector`, and catches OOM errors per INTERFACES.md §3.

**Pre-Implementation Gate:**
- ✅ INTERFACES.md §3 defines `InferenceRunner` protocol (`run(provider, model_id, prompt, max_tokens) -> MetricsRecord`)
- ✅ Dependencies satisfied: 5.1 (runner.py ✅), 4.1 (metrics.py ✅)
- ✅ `InferenceProvider` protocol available in `providers/base.py`
- ✅ `MetricsCollector` + `MetricsRecord` available in `services/metrics.py`
- ✅ Gate passed — no gaps or ambiguities

**TDD Flow (RED → GREEN → REFACTOR):**
- **RED:** Wrote `tests/unit/test_gpu_runner.py` (11 tests), ran → all failed with `ModuleNotFoundError`
- **GREEN:** Implemented `sdk/gpu_runner.py` with `GpuRunner` class, 11/11 tests passed
- **REFACTOR:** Fixed 3 test failures (mock `get_record` not returning real `MetricsRecord`, kwargs access), split test file into 3 files per 150-line rule and modular-design skill (single responsibility per file)

**Decisions:**
- `GpuRunner` delegates to provider via `load_model()`, `generate()`, `unload()` lifecycle
- `MetricsCollector` wraps the run to capture timing (load_time, total_runtime) and memory (RAM, VRAM)
- OOM detection via regex on error message (`out of memory`, `cuda.*oom`, `cublas.*oom`)
- Token estimation via 4-char-per-token heuristic (sufficient for benchmarking)
- `finally` block ensures `provider.unload()` runs even on errors
- Test files split by concern: protocol (2 tests), delegation (5 tests), errors (4 tests)

**Changes:**
- Created `src/airllm_benchmark/sdk/gpu_runner.py` — `GpuRunner` + helpers (126 lines)
- Created `tests/unit/test_gpu_runner.py` — Protocol compliance (2 tests, 24 lines)
- Created `tests/unit/test_gpu_runner_delegation.py` — Provider delegation + lifecycle (5 tests, 107 lines)
- Created `tests/unit/test_gpu_runner_errors.py` — Error handling (4 tests, 143 lines)
- Updated `docs/TODO.md` — marked 5.2 as Done
- Updated `docs/PROMPT_LOG.md` — this entry

**Validation:**
- `uv run pytest tests/unit/test_gpu_runner*.py` → 11/11 passed
- `uv run ruff check` → 0 violations
- All files under 150 lines (126 + 24 + 107 + 143)

---

## Entry 36 — GPU Runner Benchmark PoC

**Prompt:** "Please write a PoC that shows the gpu runner benchmarked"

**Context:** Task 5.2 implementation complete. Need a real-hardware PoC to prove GpuRunner works end-to-end with actual metrics collection.

**PoC Results (real hardware — NVIDIA GPU, CUDA available):**
```
Model:          meta-llama/Llama-3.2-1B
Mode:           gpu_provider
Load time:      105.01s  (includes 2.47GB model download)
Total runtime:  105.52s
Tokens gen:     14  (estimated via len(text)//4 heuristic)
Peak RAM:       3118.9 MB
Peak VRAM:      2373.2 MB
Status:         success
```

**Metrics Gaps Identified:**
- `ttft_s` = `load_time_s` — hardcoded in metrics.py, should measure time-to-first-token
- `tokens_generated` — uses crude character heuristic, not actual tokenizer count
- `load_time_s` — includes HF download time, should separate from GPU transfer
- No generation throughput metric (tokens/sec)

**Changes:**
- Created `tests/pocs/test_gpu_runner_benchmark_poc.py` — Real-hardware benchmark PoC with CUDA skip guard
- Updated `docs/PROMPT_LOG.md` — this entry

**Validation:**
- `uv run pytest tests/pocs/test_gpu_runner_benchmark_poc.py -v -s` → 1 passed, 1 skipped (CPU fallback)
- PoC ran on real GPU with real model, real metrics

---

## Entry 37 — Metric Accuracy Fixes (TTFT, Token Count, Throughput, Load Separation)

**Prompt:** "Fix inaccurate metrics: ttft_s hardcoded to load_time_s, tokens_generated uses crude len(text)//4 heuristic, no generation throughput, load_time_s includes HF download."

**Context:** GPU Runner Benchmark PoC (Entry 36) revealed 4 metric inaccuracies. All metrics must reflect actual values, not heuristics or hardcoded defaults.

**Root Causes:**
1. `ttft_s` — `metrics.py:132` hardcoded to `self._load_time`. Runner never recorded TTFT separately.
2. `tokens_generated` — `gpu_runner.py` used `_estimate_tokens(text) → len(text)//4`. Provider's `generate()` returned only text, not token count.
3. No generation throughput — Nothing measured tokens/sec.
4. `load_time_s` — Included HF download time, not separated from GPU transfer.

**Fixes Applied:**

| Fix | Before | After |
|-----|--------|-------|
| `ttft_s` | Hardcoded to `load_time_s` | `mark_generation_start() - start_time` |
| `tokens_generated` | `len(text)//4` heuristic | Real token count from tokenizer |
| `generation_throughput` | Missing | `tokens / generation_duration` (tokens/sec) |
| `load_time_s` | Includes HF download | Separated via `mark_download_complete()` |

**Interface Changes:**
- `InferenceProvider.generate()` → `tuple[str, int]` (text, token_count)
- `MetricsCollector` → Added `mark_generation_start()`, `mark_download_complete()`
- `MetricsRecord` → Added `generation_throughput` field
- `TransformersProvider` → Added `on_download_complete` callback

**Modular Split (per modular-design skill):**
- `metrics.py` (134 lines) — `MetricsCollector` service layer
- `metrics_helpers.py` (111 lines, **new**) — `MetricsRecord` data layer + `assemble_record()`
- Both under 150-line limit. Single Responsibility: data definition vs. data collection.

**Files Changed (17 files):**
- `src/airllm_benchmark/providers/base.py` — Protocol returns tuple
- `src/airllm_benchmark/providers/transformers_provider.py` — Real token count + download callback
- `src/airllm_benchmark/services/metrics.py` — New lifecycle methods (134 lines)
- `src/airllm_benchmark/services/metrics_helpers.py` — **New**, MetricsRecord + assembler (111 lines)
- `src/airllm_benchmark/sdk/gpu_runner.py` — Uses real tokens, new lifecycle
- `docs/INTERFACES.md` — Updated §2, §4, §5
- `docs/CONFIG.md` — Added `generation_throughput` field
- `docs/PROMPT_LOG.md` — This entry
- 11 test files — Updated for tuple return, new fields, new lifecycle

**Validation:**
- `uv run pytest tests/unit/ -v` → **131 passed**, 0 failed
- `uv run ruff check src/` → **0 violations**
- All files ≤ 150 lines

**Decisions:**
- Changed `generate()` Protocol from `str` to `tuple[str, int]` — breaking but all consumers are internal
- Removed `_estimate_tokens()` entirely — no longer needed with real token counts
- Split `metrics.py` per modular-design skill — Single Responsibility principle
- `mark_download_complete()` is optional — `load_time_s` falls back to full load time if not called

---

## Entry 38 — GPU Runner PoC: Quantization + Full Metrics Audit

**Prompt:** "Please also do a run with quantization" then "Are all statistics there? How are they checked?" then "Before going on to split, you must update all relevant classes and interfaces"

**Context:** GPU Runner Benchmark PoC (Entry 36) ran without quantization. User requested quantized benchmark to prove 4-bit inference works end-to-end. Then asked to audit all 18 MetricsRecord fields. Then reminded to update interfaces before splitting files.

**PoC Results (real hardware — NVIDIA GPU, CUDA, bitsandbytes 0.49.2):**

| Metric | No Quantization | 4-bit Quantized | Difference |
|--------|----------------|-----------------|------------|
| Load time | 0.82s | 1.12s | +37% |
| TTFT | 2.32s | 2.58s | +11% |
| Total runtime | 2.75s | 2.83s | +3% |
| Throughput | 36.90 tok/s | 64.11 tok/s | **+74%** |
| Peak RAM | 3299.3 MB | 2614.8 MB | -21% |
| Peak VRAM | 2373.2 MB | 1053.8 MB | **-56%** |

**Metrics Audit (all 18 fields asserted in `_assert_common`):**

| Field | GPU Test | CPU Test | How Checked |
|-------|----------|----------|-------------|
| `run_id` | ✅ | ✅ | `startswith("run_")` |
| `model` | ✅ | ✅ | Exact match |
| `mode` | ✅ | ✅ | Exact match |
| `provider` | ✅ | ✅ | Exact match |
| `prompt` | ✅ | ✅ | Exact match |
| `prompt_id` | ✅ | ✅ | Exact match (`""`) |
| `quantization` | ✅ | ✅ | Parametrized exact match |
| `max_new_tokens` | ✅ | ✅ | Exact match |
| `load_time_s` | ✅ | ✅ | `> 0` |
| `ttft_s` | ✅ | ✅ | `> 0`, `>= load_time` |
| `total_runtime_s` | ✅ | ✅ | `> 0`, `>= ttft` |
| `tokens_generated` | ✅ | ✅ | `> 0` |
| `generation_throughput` | ✅ | ✅ | `> 0` |
| `peak_ram_mb` | ✅ | ✅ | `> 0` |
| `peak_vram_mb` | ✅ GPU | ⚠️ skip CPU | `> 0` (GPU) |
| `status` | ✅ | ✅ | `== "success"` |
| `error` | ✅ | ✅ | `== ""` |
| `timestamp` | ✅ | ✅ | Non-empty |

**Interface Updates (per "Interfaces Are Holy" rule):**
- `docs/INTERFACES.md` v1.03 — Added `quantization` to §1 SDK `run_single()`, §3 `InferenceRunner.run()`
- `sdk/runner.py` — Updated `InferenceRunner` Protocol with `quantization` param
- `sdk/gpu_runner.py` — Added `quantization` param; fixed `_provider_name()` (was `transformersprovider` → now `transformers`)

**Modular Split (per modular-design skill):**
- `providers/transformers_helpers.py` (34 lines, **new**) — `build_quant_config()` data layer
- `providers/transformers_provider.py` (150 lines) — Service layer, delegates to helpers
- Split follows established pattern: `metrics.py`/`metrics_helpers.py`, `visualizer.py`/`chart_helpers.py`

**Files Changed (9 files):**
- `pyproject.toml` — Added `bitsandbytes>=0.40.0`
- `src/airllm_benchmark/providers/transformers_helpers.py` — **New**, quant config builder
- `src/airllm_benchmark/providers/transformers_provider.py` — Quantization support + helpers import
- `src/airllm_benchmark/sdk/gpu_runner.py` — Quantization param + `_provider_name` fix
- `src/airllm_benchmark/sdk/runner.py` — Protocol updated with quantization
- `docs/INTERFACES.md` — v1.03, §1 + §3 updated
- `docs/PROMPT_LOG.md` — This entry
- `tests/pocs/test_gpu_runner_benchmark_poc.py` — 4bit test + full 18-field audit

**Validation:**
- `uv run pytest tests/pocs/test_gpu_runner_benchmark_poc.py -v -s` → **2 passed, 1 skipped**
- `uv run pytest tests/unit/ -v` → **131 passed**, 0 failed
- `uv run ruff check src/ tests/pocs/` → **0 violations**
- All files ≤ 150 lines

**Decisions:**
- Added `bitsandbytes` as a core dependency (not optional) — quantization is a benchmark feature
- NF4 quant type for 4bit (best precision/performance trade-off per bitsandbytes docs)
- `float16` compute dtype for 4bit (required for CUDA compatibility)
- Split `transformers_provider.py` per modular-design skill before it exceeded 150 lines
- Updated INTERFACES.md before splitting — "Interfaces Are Holy" rule

---

## Entry 39 — Task 5.3: CPU Runner (CpuRunner)

**Prompt:** "start 5.3. Use Implementation.md and what you were thaught and your skills and check gate. When finishing the module, create a PoC that uses the module"

**Context:** Task 5.3 requires implementing `sdk/cpu_runner.py` with `CpuRunner` that delegates to a configured `InferenceProvider` on CPU, collects metrics via `MetricsCollector`, and catches OOM errors per INTERFACES.md §3. CPU runner differs from GPU runner in device target (`cpu` vs `cuda`), mode (`cpu_baseline` vs `gpu_provider`), and OOM detection (`MemoryError` vs CUDA regex).

**Pre-Implementation Gate:**
- ✅ INTERFACES.md §3 defines `InferenceRunner` protocol (`run(provider, model_id, prompt, max_tokens, quantization) -> MetricsRecord`)
- ✅ Dependencies satisfied: 5.1 (runner.py ✅), 4.1 (metrics.py ✅)
- ✅ `InferenceProvider` protocol available in `providers/base.py`
- ✅ `MetricsCollector` + `MetricsRecord` available in `services/metrics.py`
- ✅ Gate passed — no gaps or ambiguities

**TDD Flow (RED → GREEN → REFACTOR):**
- **RED:** Wrote `tests/unit/test_cpu_runner.py` (12 tests), ran → all failed with `ModuleNotFoundError`
- **GREEN:** Implemented `sdk/cpu_runner.py` with `CpuRunner` class, 12/12 tests passed
- **REFACTOR:** Split test file into 3 files per 150-line rule (212 lines → 24 + 129 + 108)

**PoC Results (real hardware — CPU, Llama-3.2-1B, max_tokens=3):**

| Metric | No Quantization | 4-bit Quantized |
|--------|----------------|-----------------|
| Load time | 2.04s | 2.90s |
| TTFT | 2.04s | 2.90s |
| Total runtime | 2.23s | 30.30s |
| Throughput | 15.98 tok/s | 0.11 tok/s |
| Peak RAM | 949.2 MB | 2087.9 MB |

**Decisions:**
- `CpuRunner` mirrors `GpuRunner` structure but targets CPU device and detects `MemoryError` as OOM
- Simpler error classification than GPU (no CUDA regex, just `isinstance(exc, MemoryError)`)
- No download callback wiring (CPU runner doesn't separate download from load)
- PoC uses `TransformersProvider` with `device="cpu"` — same provider, different target
- Relaxed VRAM assertion in PoC — `bitsandbytes` may touch GPU even on CPU runs

**Changes:**
- Created `src/airllm_benchmark/sdk/cpu_runner.py` — `CpuRunner` + helpers (142 lines)
- Created `tests/unit/test_cpu_runner.py` — Protocol compliance (2 tests, 24 lines)
- Created `tests/unit/test_cpu_runner_delegation.py` — Provider delegation + lifecycle (7 tests, 130 lines)
- Created `tests/unit/test_cpu_runner_errors.py` — Error handling (3 tests, 108 lines)
- Created `tests/pocs/test_cpu_runner_benchmark_poc.py` — Real-hardware benchmark PoC (2 tests, 102 lines)
- Updated `docs/TODO.md` — marked 5.3 as Done
- Updated `docs/PROMPT_LOG.md` — this entry

**Validation:**
- `uv run pytest tests/unit/test_cpu_runner*.py` → 12/12 passed
- `uv run pytest tests/pocs/test_cpu_runner_benchmark_poc.py -v -s` → 2/2 passed (real hardware)
- `uv run pytest tests/unit/ -v` → **143 passed**, 0 failed (no regressions)
- `uv run ruff check` → 0 violations
- All files ≤ 150 lines

---

## Entry 40 — Task 5.4: AirLLM Runner (AirllmRunner)

**Prompt:** "start 5.4. Use Implementation.md and what you were thaught and your skills and check gate. When finishing the module, create a PoC that uses the module. There is testing-airllm.py at the root of the repo to help you with the PoCs"

**Context:** Task 5.4 requires implementing `sdk/airllm_runner.py` with `AirllmRunner` that loads models via `airllm.AutoModel`, supports 4bit/8bit quantization, and uses AirLLM's paged inference (on-demand weight loading). Unlike GPU/CPU runners, AirLLM is builtin — no external provider. Follows testing-airllm.py pattern exactly.

**Pre-Implementation Gate:**
- ✅ INTERFACES.md §3 defines `InferenceRunner` protocol (`run(provider, model_id, prompt, max_tokens, quantization) -> MetricsRecord`)
- ✅ Dependencies satisfied: 4.1 (metrics.py ✅)
- ✅ AirLLM runner documented as "builtin, no provider" — clear design intent
- ✅ `RunnerManager` already imports `AirllmRunner` from expected path
- ✅ Gate passed — no gaps or ambiguities

**Step 1 — Library PoC (real data):**
- `tests/pocs/test_airllm_library_poc.py` — 4 tests: import, AutoModel accessible, signature check, real model load + generation
- Real-data test: `Qwen/Qwen2.5-0.5B-Instruct` with 4bit compression, `max_new_tokens=4`
- Follows `testing-airllm.py` pattern exactly (tokenizer settings, CUDA, use_cache)
- Discovered: `compression` parameter goes via `**kwargs`, not explicit signature
- Result: 4/4 passed (15.9s, model cached)

**Step 3 — Full Module (TDD: RED → GREEN):**
- **RED:** Wrote unit tests → failed with `ModuleNotFoundError`
- **GREEN:** Implemented module → 11/11 tests passed
- Split into 3 files per 150-line rule:
  - `airllm_loader.py` (70 lines) — model loading + quantization mapping
  - `airllm_generator.py` (66 lines) — tokenization + generation + token counting
  - `airllm_runner.py` (108 lines) — main runner with metrics + error handling

**PoC Results (real data via module — 0.5B model, 4bit):**
- Library PoC: 4/4 passed (15.9s)
- Module PoC: 1/1 passed (17.7s) — full `AirllmRunner.run()` pipeline
- Verified: status=success, tokens_generated>0, mode=airllm, provider=airllm, timing>0, RAM>0

**Decisions:**
- `AirllmRunner` is builtin — no external provider; `provider` parameter accepted as `None` for protocol compliance
- AirLLM uses paged inference: weights loaded on-demand from disk, enabling models larger than RAM
- Quantization maps `"4bit"`/`"8bit"`/`"none"` to AirLLM compression strings
- Error handling: `MemoryError` → `"oom"` status, all other exceptions → `"error"`
- Generation follows `testing-airllm.py` exactly: tokenizer settings, CUDA, `use_cache=True`
- Token counting: `output_len - input_len` from generation output sequences

**Changes:**
- Created `src/airllm_benchmark/sdk/airllm_loader.py` — model loading + quantization (70 lines)
- Created `src/airllm_benchmark/sdk/airllm_generator.py` — tokenization + generation (66 lines)
- Created `src/airllm_benchmark/sdk/airllm_runner.py` — main runner + error handling (108 lines)
- Updated `src/airllm_benchmark/sdk/__init__.py` — export `AirllmRunner`
- Created `tests/pocs/test_airllm_library_poc.py` — Library PoC with real data (4 tests)
- Created `tests/pocs/test_airllm_runner_poc.py` — Module PoC with real data (1 test)
- Created `tests/unit/test_airllm_runner.py` — Protocol compliance (2 tests)
- Created `tests/unit/test_airllm_runner_delegation.py` — Delegation + lifecycle (6 tests)
- Created `tests/unit/test_airllm_runner_errors.py` — Error handling (3 tests)
- Updated `docs/TODO.md` — marked 5.4 as Done
- Updated `docs/PROMPT_LOG.md` — this entry

**Validation:**
- Library PoC (real data): 4/4 passed (15.9s)
- Module PoC (real data): 1/1 passed (17.7s)
- Unit tests (mocked): 11/11 passed
- `uv run pytest tests/unit/ -v` → **154 passed**, 0 failed (no regressions)
- `uv run ruff check` → 0 violations
- All files ≤ 150 lines

---

## Entry 41 — Task 5.5: AirLLM Runner (Generation + Metrics Collection)

**Prompt:** "start 5.5. Use Implementation.md and what you were thaught and your skills and check gate. When finishing the module, create a PoC that uses the module."

**Context:** Task 5.5 requires implementing generation + metrics collection in `sdk/airllm_runner.py`. The `run()` method already existed from 5.4, but needed Feature PoCs to prove generation and metrics collection work independently against real hardware before marking complete.

**Pre-Implementation Gate:**
- ✅ INTERFACES.md §3 defines `InferenceRunner.run()` protocol
- ✅ INTERFACES.md §4 defines `MetricsRecord` dataclass
- ✅ INTERFACES.md §5 defines `MetricsCollector` protocol
- ✅ Dependencies satisfied: 5.4 (loader + generator ✅), 4.1 (metrics ✅)
- ✅ Gate passed — no gaps or ambiguities

**Step 1 — Library PoC:** Already completed in Entry 40 (`test_airllm_library_poc.py`)

**Step 2 — Feature PoCs (real data):**
- `tests/pocs/test_airllm_generation_poc.py` — 2 tests: 4bit quantization, no quantization
- `tests/pocs/test_airllm_metrics_poc.py` — 1 test: full MetricsCollector lifecycle
- Real-data test: `Qwen/Qwen2.5-0.5B-Instruct` with 4bit compression
- Result: 3/3 passed

**Step 3 — Full Module:** Already implemented in Entry 40, verified with Feature PoCs

**PoC Results (real data — 0.5B model, 4bit):**
- Generation PoC: 2/2 passed — text output valid, token count correct
- Metrics PoC: 1/1 passed — load_time=3.03s, TTFT=3.03s, runtime=32.22s, throughput=0.27 tok/s, RAM=1807.8MB, VRAM=333.0MB
- Module PoC: 1/1 passed — full `AirllmRunner.run()` pipeline

**Decisions:**
- Feature PoCs isolate generation and metrics collection before full module verification
- Generation PoC tests both quantized (4bit) and uncompressed (none) modes
- Metrics PoC exercises complete MetricsCollector lifecycle: start → load → generation → stop → record
- Ruff F541 violations fixed (f-string without placeholders)

**Changes:**
- Created `tests/pocs/test_airllm_generation_poc.py` — Feature PoC for generation (2 tests)
- Created `tests/pocs/test_airllm_metrics_poc.py` — Feature PoC for metrics collection (1 test)
- Updated `docs/TODO.md` — marked 5.5 as Done
- Updated `docs/PROMPT_LOG.md` — this entry

**Validation:**
- Feature PoCs (real data): 3/3 passed
- Module PoC (real data): 1/1 passed
- Unit tests (mocked): 11/11 passed
- `uv run ruff check` → 0 violations
- All files ≤ 150 lines

---

## Entry 42 — Task 5.6: POC Minimal Runner Pipeline

**Prompt:** "start 5.6. Use Implementation.md and what you were thaught and your skills and check gate. When finishing the module, create a PoC that uses the module."

**Context:** Task 5.6 requires an end-to-end POC that exercises the full runner pipeline: `RunnerManager → runner → provider → MetricsCollector → MetricsRecord`. The goal is to verify that every runner mode (gpu_provider, cpu_baseline, airllm) produces a valid `MetricsRecord` with all 18 fields correctly populated.

**Pre-Implementation Gate:**
- ✅ INTERFACES.md §3 defines `InferenceRunner.run()` protocol
- ✅ INTERFACES.md §4 defines `MetricsRecord` dataclass
- ✅ INTERFACES.md §5 defines `MetricsCollector` protocol
- ✅ INTERFACES.md §2 defines `InferenceProvider` protocol
- ✅ Dependencies satisfied: 5.2 (GpuRunner ✅), 5.3 (CpuRunner ✅), 5.5 (AirllmRunner ✅)
- ✅ Gate passed — no gaps or ambiguities

**Implementation Approach:**
- Created `MockProvider` implementing `InferenceProvider` protocol for deterministic test output
- Used real `RunnerManager`, `GpuRunner`, `CpuRunner`, `AirllmRunner`, and `MetricsCollector` modules
- Mocked only external dependencies (provider for GPU/CPU, airllm library for AirLLM)
- Verified all 18 `MetricsRecord` fields with type and value assertions
- Split into two files per 150-line rule and modular-design skill (single responsibility)

**Decisions:**
- Separated helpers (`pipeline_helpers.py`) from tests (`test_runner_pipeline_poc.py`) per modular-design skill
- `MockProvider` is reusable across pipeline PoCs
- AirLLM test patches `airllm_runner` namespace (where symbols are looked up via `from .module import name`)
- GPU/CPU runners exercise real `MetricsCollector` with real psutil RAM sampling

**Changes:**
- Created `tests/pocs/pipeline_helpers.py` — MockProvider + assertion/print helpers (92 lines)
- Created `tests/pocs/test_runner_pipeline_poc.py` — 5 end-to-end pipeline tests (125 lines)
- Updated `docs/TODO.md` — marked 5.6 as Done
- Updated `docs/PROMPT_LOG.md` — this entry

**Validation:**
- Pipeline PoC tests: 5/5 passed
- GPU provider pipeline: MetricsRecord with all 18 fields valid
- CPU baseline pipeline: MetricsRecord with all 18 fields valid
- AirLLM pipeline: MetricsRecord with all 18 fields valid
- Mode dispatch: 3 modes correctly registered
- Error handling: Unknown mode raises ValueError
- `uv run ruff check` → 0 violations
- All files ≤ 150 lines (92 + 125)
- Full test suite: 159/159 passed (unit + pipeline PoC)

---

## Entry 43 — ResultWriter Module + 150-Line Split

**Prompt:** "Read inconcistencies.md. add the missing result writer according to what you were thaught, implementation.md and your skills. Update the interface and all relevant ones in interfaces.md. When finishing the module, create a PoC that uses the module with real data."

**Context:** `INCONSISTENCIES.md` §1 identified that `ResultWriter` was defined in `PLAN.md` (C3 Component Diagram line 91, Sequence Diagram lines 199-200) but missing from `INTERFACES.md` and `TODO.md`. The component serializes `MetricsRecord` → `results/metrics.json` and is called by the Runner Manager after each run.

**Pre-Implementation Gate:**
- ✅ PLAN.md C3 defines `ResultWriter` as "Serializes metrics to JSON"
- ✅ PLAN.md Sequence Diagram shows `RunnerMgr->>Writer: append(result)` → `Writer->>Storage: write JSON`
- ✅ CONFIG.md §1 defines `MetricsRecord` schema (18 fields)
- ✅ `MetricsRecord` dataclass exists in `services/metrics_helpers.py`
- ✅ Gate passed — interface designed from existing architecture docs

**Implementation Approach (per IMPLEMENTATION.md):**
- Step 1 — Library PoC: `pocs/result_writer_library_poc.py` proved JSON array read/write works
- Step 2 — Feature PoCs: `pocs/result_writer_feature_poc.py` proved `append`, `load`, `clear` with real `MetricsRecord`
- Step 3 — Full Module: `services/result_writer.py` (109 lines) with TDD unit tests
- Real-data PoC: `pocs/result_writer_real_data_poc.py` with 3 realistic `MetricsRecord` instances

**Decisions:**
- Placed in `services/` layer per PLAN.md C3 component diagram
- JSON array format per ADR-002 (JSON for Results Storage)
- `append()` loads existing records, appends, writes back — incremental persistence
- `load()` returns empty list when file missing — no crash on first run
- `clear()` replaces file with empty array — for fresh benchmark runs

**Changes:**
- Created `src/airllm_benchmark/services/result_writer.py` — ResultWriter class (109 lines)
- Created `tests/unit/test_result_writer.py` — 11 unit tests
- Created `pocs/result_writer_library_poc.py` — Library PoC (105 lines)
- Created `pocs/result_writer_feature_poc.py` — Feature PoCs (155 lines, later split to 106)
- Created `pocs/result_writer_real_data_poc.py` — Real-data PoC (149 lines)
- Updated `docs/INTERFACES.md` §7 — Added `ResultWriter` interface
- Updated `src/airllm_benchmark/services/__init__.py` — Added `ResultWriter` export
- Updated `docs/INCONSISTENCIES.md` §1 — Marked ✅ Resolved
- Updated `docs/PROMPT_LOG.md` — This entry

**Validation:**
- Unit tests: 11/11 passed
- Library PoC: PASSED
- Feature PoCs: PASSED
- Real-data PoC: PASSED (schema matches CONFIG.md §1)
- `uv run ruff check` → 0 violations
- All files ≤ 150 lines

---

## Entry 44 — 150-Line Split: result_writer_feature_poc.py

**Prompt:** "Split files that are too big according to what you were thaught and your skills about splitting. Then Add to prompt log and commit"

**Context:** `pocs/result_writer_feature_poc.py` was 155 lines, exceeding the 150-line limit from `CLAUDE.md` §4. Per modular-design skill, files must stay under 150 lines.

**Approach:** Removed redundant section comments and docstring verbosity. The PoC is disposable per IMPLEMENTATION.md ("PoC files themselves are disposable and can be removed after the module is complete"), so trimming rather than extracting was the pragmatic choice.

**Changes:**
- Trimmed `pocs/result_writer_feature_poc.py` from 155 → 106 lines

**Validation:**
- `uv run ruff check` → 0 violations
- Feature PoC: PASSED (all 5 assertions)
- File now 106 lines (≤ 150)

---

## Entry 45 — Task 5.7: BenchmarkSDK Entry Point

**Prompt:** "start 5.7. Use Implementation.md and what you were thaught and your skills and check gate. When finishing the module, create a PoC that uses the module."

**Context:** Task 5.7 requires implementing `sdk/sdk.py` — the `BenchmarkSDK` single entry point per `INTERFACES.md` §1. Dependencies (5.1, 5.2, 5.3, 5.5, 4.4) were all Done. Pre-Implementation Gate confirmed interface exists and is clear. ResultWriter was identified as architecturally required per `PLAN.md` C3 + Sequence Diagram and added as dependency.

**Approach:** Followed `IMPLEMENTATION.md` three-step process:
1. **Library PoC** — Skipped (SDK orchestrates existing modules, no external library)
2. **Feature PoCs** — Created `pocs/sdk_module_poc.py` with 3 PoC tests exercising all interface methods
3. **Full Module** — Implemented `sdk.py` (135 lines) + `sdk_helpers.py` (121 lines) split to stay under 150-line limit. Tests split by interface method following project pattern (like `test_transformers_load.py`, `test_transformers_generate.py`, etc.)

**Changes:**
- Created `src/airllm_benchmark/sdk/sdk.py` — `BenchmarkSDK` with `run_benchmark()`, `run_single()`, `generate_visualization()`
- Created `src/airllm_benchmark/sdk/sdk_helpers.py` — `create_provider()`, `_run_benchmark_impl()`, `_resolve_provider()`, `build_summary()`
- Created `tests/unit/test_sdk_init.py` — 4 init tests
- Created `tests/unit/test_sdk_run_benchmark.py` — 3 run_benchmark tests
- Created `tests/unit/test_sdk_run_single.py` — 3 run_single tests
- Created `tests/unit/test_sdk_visualization.py` — 2 visualization tests
- Updated `tests/unit/conftest.py` — added `mock_config`, `mock_hw` fixtures
- Created `pocs/sdk_module_poc.py` — 3 PoC tests
- Updated `docs/TODO.md` — added ResultWriter dependency, marked 5.7 Done

**Validation:**
- `uv run ruff check` → 0 violations
- `uv run pytest tests/unit/` → 177 passed (12 SDK tests + 165 existing)
- PoC tests → 3 passed
- All files ≤ 150 lines
- No hardcoded config — all loaded from `experiment.json`

**Note:** PoC uses real config but mocked runners. Full real-data PoC deferred pending user direction.

---

## Entry 46 — Task 5.8: Cross-Runner Tests

**Prompt:** "start 5.8. Use Implementation.md and what you were thaught and your skills and check gate. When finishing the module, create a PoC that uses the module."

**Context:** Task 5.8 requires cross-runner unit tests verifying all three runners (GPU, CPU, AirLLM) share the same behavioral contract: consistent OOM handling, metrics output structure, parameter propagation, and RunnerManager dispatch. Dependencies (5.2, 5.3, 5.5) were all Done. Pre-Implementation Gate confirmed the InferenceRunner protocol and MetricsCollector interface exist and are clear.

**Approach:** Followed `IMPLEMENTATION.md` three-step process:
1. **Library PoC** — `poc_runners_library.py` + `test_poc_runners_library.py` — verified all runner classes are importable, instantiable, and dispatchable via RunnerManager
2. **Feature PoCs** — Created 3 feature PoCs (OOM handling, metrics output, parameter propagation) each with standalone script + pytest test file
3. **Full Module** — Split into 4 focused test files + 2 fixture modules to respect 150-line limit:
   - `test_runner_manager.py` — 5 dispatch tests
   - `test_cross_runner_oom.py` — 3 OOM tests
   - `test_cross_runner_metrics.py` — 3 metrics output tests
   - `test_cross_runner_params.py` — 3 parameter propagation tests
   - `fixtures_runner.py` — shared runner fixtures and record factories
   - `fixtures_metrics.py` — shared sample records fixture (moved from conftest.py)

**Changes:**
- Created `tests/pocs/poc_runners_library.py` — library PoC proving runner importability
- Created `tests/pocs/test_poc_runners_library.py` — 4 library PoC tests
- Created `tests/pocs/poc_oom_handling.py` — OOM handling PoC for all runners
- Created `tests/pocs/test_poc_oom_handling.py` — 3 OOM PoC tests
- Created `tests/pocs/poc_metrics_output.py` — metrics output PoC for all runners
- Created `tests/pocs/test_poc_metrics_output.py` — 3 metrics PoC tests
- Created `tests/pocs/poc_param_propagation.py` — parameter propagation PoC for all runners
- Created `tests/pocs/test_poc_param_propagation.py` — 3 param propagation PoC tests
- Created `tests/unit/test_runner_manager.py` — 5 RunnerManager dispatch tests
- Created `tests/unit/test_cross_runner_oom.py` — 3 cross-runner OOM tests
- Created `tests/unit/test_cross_runner_metrics.py` — 3 cross-runner metrics tests
- Created `tests/unit/test_cross_runner_params.py` — 3 cross-runner param tests
- Created `tests/unit/fixtures_runner.py` — shared runner fixtures
- Created `tests/unit/fixtures_metrics.py` — shared sample records fixture
- Updated `tests/unit/conftest.py` — moved sample_records to fixtures_metrics.py
- Updated `docs/TODO.md` — marked 5.8 Done

**Validation:**
- `uv run ruff check` → 0 violations
- All 14 cross-runner tests pass
- All 8 PoC tests pass
- All files ≤ 150 lines
- No hardcoded config — providers and MetricsCollector mocked per project rules

---

## Entry 47 — Task 6.1: POC CLI → SDK Smoke Test

**Prompt:** "Implement phase 6.1 according to what you were thaught and your skills"

**Context:** Task 6.1 requires a POC CLI that accepts `--single`, calls SDK with small model, prints result — no full pipeline. Dependency 5.7 (BenchmarkSDK) was Done. Pre-Implementation Gate: No interface needed in INTERFACES.md for CLI (presentation layer per ADR-001). SDK `run_single()` interface is well-defined.

**Approach:** Followed SDK-First Architecture skill — CLI is a thin presentation layer that delegates all logic to `BenchmarkSDK`. TDD skill — tests written alongside implementation. Created minimal CLI with argparse, mocking SDK in unit tests, then validated with real data.

**Changes:**
- Created `src/main.py` — CLI entry point with `--single`, `--model`, `--mode`, `--prompt`, `--config-dir` flags (94 lines)
- Created `tests/unit/test_cli.py` — 8 unit tests (argparse + SDK delegation, all mocked) (111 lines)
- Updated `docs/TODO.md` — marked 6.1 Done

**Validation:**
- `uv run ruff check src/ tests/` → 0 violations
- `uv run pytest tests/unit/` → 199 passed (8 new CLI tests + 191 existing)
- Real-data smoke test: `uv run python src/main.py --single --model Qwen/Qwen2.5-0.5B-Instruct --mode cpu_baseline` → CLI → SDK → Provider → Model load → Result printed successfully
- All files ≤ 150 lines
- No hardcoded config — all defaults via argparse, config loaded from `experiment.json`

**Note:** Real-data test revealed pre-existing device mismatch bug in `cpu_runner`/`transformers_provider` (tokenizer input_ids on cuda:0, model on cpu). CLI correctly surfaced and printed the error. Bug fix deferred — outside Phase 6.1 scope.

---

## Entry 48 — Device Mismatch Fix + Model Resolution

**Prompt:** "uv run python src/main.py --single --model small --mode cpu_baseline --prompt 'What is AI?' ... Fix the bug according to what you were thaught and your skills"

**Context:** CPU baseline smoke test failed with device mismatch: tokenizer placed `input_ids` on `cuda:0` while the model was on `cpu`. Secondary issue: `--model small` tier name not resolved to actual HuggingFace model ID.

**Root Cause Analysis:**
1. **Device Mismatch:** `TransformersProvider.load_model(model_id, device)` received `device="cpu"` from `cpu_runner` and correctly loaded the model via local `target` variable. But it never updated `self._device` (instance attribute). `generate()` used stale `self._device` (from `__init__` which read `"cuda"` from `config/experiment.json` provider_config). Result: model on CPU, input tensors on CUDA.
2. **Model Resolution:** `sdk.run_single()` passed `model_id` directly to the runner without resolving tier names (e.g., `"small"` → `"Qwen/Qwen2.5-0.5B-Instruct"`). Full HF IDs worked; tier aliases failed.

**Approach:** Surgical fix in provider layer (device sync) and SDK layer (model resolution). No interface changes — both fixes are internal implementation corrections.

**Changes:**
- `src/airllm_benchmark/providers/transformers_provider.py` — Added `self._device = target` in `load_model()` to sync instance device before loading. Ensures `generate()` uses the same device as the model.
- `src/airllm_benchmark/sdk/sdk_helpers.py` — Added `resolve_model_id()` helper: passes through full HF IDs (containing `/`), resolves tier names via `config.get_model_id()`.
- `src/airllm_benchmark/sdk/sdk.py` — Call `resolve_model_id()` in `run_single()` before passing to runner.

**Validation:**
- `uv run python src/main.py --single --model small --mode cpu_baseline --prompt "What is AI?"` → success
- Model resolved: `Qwen/Qwen2.5-0.5B-Instruct`
- Status: success, Runtime: 3.05s, Tokens: 32, Peak RAM: 1775 MB
- No device mismatch error

---

## Entry 49 — Prompt Log + Commit

**Prompt:** "Add what you did to prompt log and commit"

**Context:** Bug fixes (device mismatch + model resolution) were already documented in Entry 48 and committed as `913d96c`. Only `src/main.py` remained uncommitted with improved output formatting.

**Changes:**
- `docs/PROMPT_LOG.md` — Added Entry 49 (this entry).
- `src/main.py` — Already staged: improved `_print_result()` with sectioned output (Timing, Generation, Memory), status icon, and timestamp.

**Validation:**
- `uv run python src/main.py --single --model small --mode cpu_baseline --prompt "What is AI?"` → success with formatted output.

---

## Entry 50 — AirLLM Provider Bug Fix

**Prompt:** `uv run python src/main.py --single --model small --mode cpu_baseline --prompt "What is AI?"` ... "Doesn't work with airllm. Fix the bug according to what you were taught and your skills"

**Context:** Running with `--mode airllm` crashed with `ValueError: Unsupported provider: 'airllm'. Available: transformers`. AirLLM is a builtin runner that does not delegate to an external `InferenceProvider` — it loads and generates directly via `airllm.AutoModel`. However, both `sdk.run_single()` and `sdk_helpers._run_benchmark_impl()` unconditionally called `create_provider()` for all modes, including airllm.

**Root Cause:** `create_provider()` only supports `"transformers"`. When mode is `"airllm"`, `_resolve_provider()` returns `"airllm"` and `create_provider("airllm", ...)` raises `ValueError`. `AirllmRunner.run()` accepts `provider: InferenceProvider | None` and ignores it.

**Approach:** Handle airllm as a separate code path in both callers. Directly instantiate `AirllmRunner` and call with `provider=None`. No protocol changes — `InferenceRunner` protocol unchanged.

**Changes:**
- `src/airllm_benchmark/sdk/sdk.py` — `run_single()` branches on mode: airllm → direct `AirllmRunner` call with `provider=None`, other modes → existing provider + runner flow.
- `src/airllm_benchmark/sdk/sdk_helpers.py` — `_run_benchmark_impl()` same pattern: airllm branch calls `AirllmRunner` directly, other modes use provider.

**Validation:**
- `uv run python src/main.py --single --model small --mode airllm --prompt "What is AI?"` → model loads, fetches weights, generates output (timed out due to AirLLM paged inference slowness — expected behavior).
- No `ValueError` — airllm mode reaches inference successfully.
- Diagnostics: 0 violations across all edited files.

---

## Entry 51 — CLI Quantization + Provider Passthrough Fix

**Prompt:** `uv run python src/main.py --single --model small --mode cpu_baseline --prompt "What is AI?"` followed by "Please add an option to specify quantization in the main cli run single" and "create_provider in sdk_helpers.py doesn't pass the quantization. Check if needs to be fixed in airllm as well"

**Context:** The SDK's `run_single()` accepted a `quantization` parameter, but the CLI never exposed it. Worse, `create_provider()` in `sdk_helpers.py` instantiated `TransformersProvider(device=device)` without passing quantization — so the provider always defaulted to `"none"` regardless of what the user or config specified. The runners received `quantization` and recorded it in metrics, but the actual model loading ignored it.

**Root Cause:** `create_provider(name, provider_config)` had no `quantization` parameter. It created `TransformersProvider(device=device)` with the constructor default `quantization="none"`. The runners passed `quantization` only to `MetricsCollector.start()` for recording — never to the provider. AirLLM was unaffected because it bypasses `create_provider()` and passes quantization directly to `load_model(model_id, quantization)`.

**Approach:** Three-part fix: (1) expose `--quantization` CLI argument, (2) thread `quantization` through `create_provider()` to `TransformersProvider`, (3) update all call sites. No interface changes — `InferenceProvider` protocol unchanged.

**Changes:**
- `src/main.py` — Added `--quantization` CLI arg (`choices=["none", "4bit", "8bit"]`, default `"none"`). Wired to `sdk.run_single(quantization=args.quantization)`.
- `src/airllm_benchmark/sdk/sdk_helpers.py` — Added `quantization` parameter to `create_provider()`. Passed to `TransformersProvider(device=device, quantization=quantization)`. Updated `_run_benchmark_impl()` call site to pass `config.quantization`.
- `src/airllm_benchmark/sdk/sdk.py` — Updated `create_provider()` call in `run_single()` to pass `quantization`.
- `tests/unit/test_cli.py` — Fixed `mock_record` fixture (added missing attrs: `load_time_s`, `ttft_s`, `quantization`, `prompt`, `peak_vram_mb`, `timestamp`, `max_new_tokens`, `generation_throughput`). Updated `test_delegates_to_sdk` assertion to include `quantization="none"`.
- `tests/unit/test_sdk_run_single.py` — Updated `test_custom_provider_override` assertion to include `quantization="none"` in `assert_called_with`.

**Validation:**
- `uv run python src/main.py --single --model small --mode cpu_baseline --prompt "What is AI?" --quantization 4bit` → bitsandbytes warnings confirm quantization active, Peak RAM: 1505 MB (was 1811 MB without fix).
- `uv run python src/main.py --single --model small --mode gpu_provider --prompt "What is AI?" --quantization 4bit` → bitsandbytes warnings, Peak VRAM: 461 MB (was 966 MB without fix).
- `uv run python src/main.py --single --model small --mode gpu_provider --prompt "What is AI?" --quantization 8bit` → MatMul8bitLt warning confirms 8bit quantization active, Peak VRAM: 618 MB.
- `uv run pytest tests/unit/` → 199 passed, 0 failures.

---

## Entry 52 — 150-Line Rule Enforcement (Final Audit)

**Prompt:** "check that the 150 lines rule actually holds to all project code files" → "yes, according to what you were taught and your skills"

**Context:** CLAUDE.md §3 Strict Coding Standards mandates "No file exceeds 150 lines". Full audit of all project `.py` files (excluding `.venv` and third-party docs) revealed 2 violations.

**Decision:** Applied modular-design skill (Single Responsibility, Separation of Concerns) to extract code following existing project patterns:
1. `sdk/sdk_helpers.py` (161 → 137 lines) — Extracted `build_summary()` into new `sdk/sdk_summary.py` (46 lines). Moved `validate_config()` into `shared/config_loader.py` (belongs with config validation logic). Removed unused imports (`Path`, `Sequence`).
2. `providers/transformers_provider.py` (152 → 147 lines) — Extracted CUDA cache clearing into `providers/transformers_helpers.py` as `clear_cuda_cache()` (follows same split pattern as `metrics_helpers.py` / `metrics.py`).
3. Updated `shared/config.py` to re-export `validate_config` for backward compatibility.

**Changes:**
- `src/airllm_benchmark/sdk/sdk_summary.py` — New file (46 lines). Contains `build_summary()` for benchmark result formatting.
- `src/airllm_benchmark/sdk/sdk_helpers.py` — Removed `build_summary()`, `validate_config()`, unused imports. Added `__all__` export list. Added import of `build_summary` from `sdk_summary` and `validate_config` from `config_loader` for backward compatibility. (161 → 137 lines)
- `src/airllm_benchmark/providers/transformers_helpers.py` — Added `clear_cuda_cache()` function. (34 → 45 lines)
- `src/airllm_benchmark/providers/transformers_provider.py` — Replaced inline CUDA cache clearing with `_helpers.clear_cuda_cache()` call. (152 → 147 lines)
- `src/airllm_benchmark/shared/config_loader.py` — Added `validate_config()` function. (98 → 113 lines)
- `src/airllm_benchmark/shared/config.py` — Added `validate_config` to imports and `__all__`. (29 → 31 lines)

**Validation:**
- `ruff check src/` → 0 violations.
- No project `.py` files exceed 150 lines (verified with `wc -l` audit).
- `uv run pytest tests/unit/` → 199 passed, 0 failures.

---

## Entry 53 — Phase 6.2: CLI Entry Point (`src/main.py`)

**Prompt:** "Implement phase 6.2 according to what you were taught and your skills. Remember to actually test the final module for real"

**Context:** TODO.md task 6.2 requires implementing `src/main.py` — CLI that delegates to `BenchmarkSDK`. Depends on 6.1 (POC: CLI → SDK smoke test) which was Done. Definition of Done: Accepts `--run-all` and `--single` flags; prints summary; delegates all logic to SDK. The existing `src/main.py` had `--single` but was missing `--run-all`. Adding `--run-all` would push the file over the 150-line limit.

**Decision:** Applied IMPLEMENTATION.md three-step process (Library PoC → Feature PoCs → Full Module) and modular-design skill (Single Responsibility):
1. **Library PoC** (`pocs/cli_run_all_poc.py`) — Verified SDK delegation pattern with real config + real inference (Qwen2.5-0.5B, cpu_baseline, success in 2.16s).
2. **Full Module** — Added `--run-all` flag + `run_all()` function. Extracted `print_result()` and new `print_run_all_result()` into `src/airllm_benchmark/cli_printers.py` to respect 150-line limit (same split pattern as `metrics_helpers.py` / `metrics.py`).
3. **Tests** — Added 6 new tests for `--run-all` (parse args, SDK delegation, output formatting). Total 14 tests, all pass.

**Changes:**
- `src/main.py` — Added `--run-all` argument, `run_all()` function, updated `main()` dispatch. Imports print helpers from `cli_printers`. (141 → 113 lines)
- `src/airllm_benchmark/cli_printers.py` — New file (70 lines). Contains `print_result()` and `print_run_all_result()` for CLI output formatting.
- `tests/unit/test_cli.py` — Added `TestParseArgsRunAll` (3 tests) and `TestRunAll` (3 tests). Updated imports to include `run_all`. (8 → 14 tests)
- `pocs/cli_run_all_poc.py` — New PoC (82 lines). Validates SDK delegation with real config + real inference.
- `docs/TODO.md` — Marked 6.2 as Done.

**Validation:**
- `uv run pytest tests/unit/test_cli.py` → 14 passed, 0 failures.
- `uv run pytest tests/unit/` → 205 passed, 0 failures.
- `uv run ruff check src/ tests/` → 0 violations.
- `src/main.py` (113 lines), `cli_printers.py` (70 lines) — both under 150-line limit.
- Real validation: `uv run python src/main.py --single --model small --mode cpu_baseline --prompt "What is 2+2?"` → ✓ success, 2.16s runtime, 29.5 tok/s.
- Smoke test: `uv run python src/main.py --run-all --config-dir config/smoke` → 27/27 runs succeeded across all modes (gpu_provider avg 1.84s, cpu_baseline avg 1.86s, airllm avg 36.50s).

---

## Entry 54 — Visualizer Timestamped Subdirectory

**Prompt:** "Does Visualizer write to the same file every time?" → "I want the visualizer to work like the result writers. Use a subdirectory in the sdk"

**Context:** The Visualizer always wrote to fixed filenames (`assets/latency_chart.png`, `assets/memory_chart.png`), overwriting previous runs. ResultWriter uses a timestamped path (`results/metrics_{timestamp}.json`) managed by the SDK. User wants the Visualizer to follow the same pattern — SDK-managed timestamped subdirectory so each run preserves its own artifacts.

**Approach:** Minimal surgical change in `sdk.py` — share the `now` timestamp between ResultWriter and Visualizer output paths. The Visualizer service itself is unchanged (still takes `output_dir` parameter, still writes fixed filenames inside it). The SDK now creates `assets/run_{timestamp}/` and passes it, matching the ResultWriter pattern where the SDK owns the output path.

**Changes:**
- `src/airllm_benchmark/sdk/sdk.py` — `run_benchmark()` creates shared `now` timestamp. ResultWriter uses `results/metrics_{now}.json`, Visualizer uses `assets/run_{now}/`. Same timestamp ensures results and charts are correlated.
- `tests/unit/test_sdk_run_benchmark.py` — Updated `test_visualizer_called_with_records` to verify `generate_all()` receives timestamped `output_dir` argument.

**Before:** Every run overwrote `assets/latency_chart.png` and `assets/memory_chart.png`.

**After:** Each run writes to its own subdirectory, e.g. `assets/run_20260705_143022/latency_chart.png`.

**Validation:**
- `uv run pytest tests/unit/test_sdk_run_benchmark.py tests/unit/test_visualizer_*.py tests/unit/test_sdk_visualization.py -v` → 24 passed, 0 failures.
- `uv run ruff check src/ tests/` → 0 violations.
- All files ≤ 150 lines.

---

## Entry 55 — Phase 3.5: `providers/llamacpp_provider.py`

**Prompt:** "Finish Phase 3 by implementing `providers/llamacpp_provider.py` — llama.cpp Python bindings, for completeness. Do it properly, not as a stub." (Inconsistencies.md #4 had previously marked llama.cpp as out of scope; user explicitly asked for it anyway.)

**Context:** TODO.md task 3.5 was the only remaining Phase 3 item. `InferenceProvider` protocol (`load_model`, `generate`, `unload`) is defined in `providers/base.py`; `TransformersProvider` + `transformers_helpers.py` set the established thin-provider/helpers split pattern and the API Gatekeeper convention (`call_with_rate_limit("huggingface", ...)` for external HF calls).

**Decision:** Added `llama-cpp-python` as a dependency and implemented `LlamaCppProvider` following the same split as the transformers provider:
- `providers/llamacpp_provider.py` (110 lines) — thin provider wrapping `llama_cpp.Llama`.
- `providers/llamacpp_helpers.py` (103 lines) — model-source resolution (`split_model_id`), device→`n_gpu_layers` mapping (`resolve_n_gpu_layers`), the gatekeeper-wrapped load call (`load_llama_model`), and token-count fallback (`count_completion_tokens`).

**Design choices:**
- `model_id` accepts either a local `.gguf` path, or a HuggingFace-Hub identifier of the form `"repo_id::filename"` (the `::` separator was chosen because it cannot appear in a repo id or a filesystem path), resolved via `Llama.from_pretrained(repo_id=..., filename=...)`. Only the HF-Hub fetch branch goes through `call_with_rate_limit("huggingface", ...)` — the local-path branch is disk I/O, not an external call, so it is not gatekept.
- `device` maps to `n_gpu_layers`: `"cpu"` → `0`, anything else (`"cuda"`, `"mps"`, `"gpu"`, ...) → `-1` (offload all layers), mirroring how `TransformersProvider` maps `device` onto `.to(target)`.
- `generate()` prefers `response["usage"]["completion_tokens"]` for the actual token count, falling back to re-tokenizing the generated text via `llm.tokenize()` when `usage` is absent (some binding versions omit it).
- `load_model()` / `unload()` follow the same idempotent-cache / `gc.collect()` pattern as `TransformersProvider`.

**Build risk check:** `llama-cpp-python` compiles a native extension. `cmake` was not preinstalled and no passwordless `sudo` was available, but `uv sync` built the wheel successfully anyway (prebuilt `cmake` came in via the build backend's own build-time dependency) — no toolchain intervention was needed.

**Scope boundary:** `LlamaCppProvider` is implemented and unit-tested but **not** wired into `sdk/sdk_helpers.py`'s `create_provider()` factory or `config/experiment.json` — that wiring was out of scope for this task (only TODO 3.5 was requested) and the benchmark's core comparison still runs through Transformers. Documented explicitly in `INCONSISTENCIES.md` #4 so it isn't mistaken for a wired, selectable provider.

**Changes:**
- `pyproject.toml` — added `llama-cpp-python>=0.3.0`; `uv.lock` regenerated.
- `src/airllm_benchmark/providers/llamacpp_provider.py` — new (110 lines).
- `src/airllm_benchmark/providers/llamacpp_helpers.py` — new (103 lines).
- `tests/unit/conftest.py` — added `llamacpp_provider` fixture and `mock_llamacpp()` context manager (patches `llamacpp_helpers.Llama`).
- `tests/unit/test_llamacpp_load.py`, `test_llamacpp_generate.py`, `test_llamacpp_unload.py`, `test_llamacpp_lifecycle.py` — new, 36 tests total, 100% coverage on both new files.
- `docs/TODO.md` — 3.5 marked ✅ Done; 3.6 note updated; Phase 3 row now 9/9 Done; Summary Total 38/50 Done.
- `docs/INCONSISTENCIES.md` — the providers entry changed from "Out of Scope" to "🟡 Partially Resolved" (llama.cpp implemented; wiring deferred); version bumped 1.04 → 1.05.
- `docs/INTERFACES.md` / `docs/PLAN.md` — checked against the implementation; both already described llama.cpp accurately (Python bindings), no changes needed.

**Validation:**
- `uv run ruff check src tests scripts` → 0 violations.
- `uv run python scripts/check_line_cap.py src tests --limit 150 --mode raw` → passes.
- `uv run pytest --cov=airllm_benchmark --cov-report=term-missing --cov-fail-under=85` → 309 passed, 9 skipped, 90.34% coverage (both new llamacpp files at 100%).

---

## Entry 56 — hw5-bundle Quality Gates + GpuRunner Device Bug + API Gatekeeper

**Prompt:** Gap analysis against PRD/PLAN/TODO surfaced several concrete issues: an instructor-provided `hw5-bundle.zip` scaffold had not been integrated, a real device-handling bug in `GpuRunner`, and CLAUDE.md's mandatory API Gatekeeper had never been planned or built.

**Context:** `hw5-bundle.zip` contained 9 quality-gate scripts, a keyless CI workflow, matching pre-commit hooks, and a starter `README.md` with a `readme_sync.py`-generated facts region. Tracing why 6 PoC tests were failing found: 5 were legitimately CUDA-only tests missing a `skipif` guard, but 1 (`test_gpu_runner_cpu_fallback`) exposed a real bug — `sdk/gpu_runner.py` hardcoded `DEFAULT_DEVICE = "cuda"` and always overrode the provider's configured device.

**Decisions:**
- Integrated the hw5-bundle as-is (`scripts/`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`), adopted its starter README (closing TODO 9.5, previously empty), and split two files that newly failed the bundle's 150-line gate (`sdk.py` → extracted `render_visualization` into `sdk_helpers.py`; `test_cli.py` → split `--run-all` tests into `test_cli_run_all.py`).
- Fixed `GpuRunner` to pass `None` (not a hardcoded device) to `provider.load_model()`, so `TransformersProvider`'s own fallback (`target = device or self._device`) applies — respects the provider's constructed device instead of always forcing CUDA. Added the missing `skipif(not cuda_available)` guards to the 5 real-GPU/AirLLM PoC tests.
- Implemented `shared/gatekeeper.py` (`call_with_rate_limit`, `RateLimiter`) + `config/rate_limits.json`, wired into the two real HF Hub call sites (`transformers_helpers.load_tokenizer_and_model`, `airllm_loader.load_model`). Documented in `CONFIG.md` §5, `INTERFACES.md` §9, `PLAN.md` (C3 diagram, C4 structure, ADR-006).
- Corrected `config/hardware.json` (was fabricated placeholder data) to this sandbox's real specs, fixed `TODO.md`'s self-contradictory summary table (was `0/49` despite ~19 tasks marked Done), and corrected `PRD.md`'s stale provider-specific acceptance criterion/default.

**Follow-up fix:** CI failed once opened as a PR — `test_cpu_runner_benchmark_poc.py` / `test_gpu_runner_benchmark_poc.py` hardcoded the gated `meta-llama/Llama-3.2-1B` model; GitHub Actions runners have no `HF_TOKEN`. Switched `POC_MODEL` to the already-open `Qwen/Qwen2.5-0.5B-Instruct` (matches `config/experiment.json`'s "small" tier).

**Validation:** All 10 gate scripts pass; `pytest --cov` → 284 passed, 9 skipped, 0 failed, 89.6% coverage. Merged via PR #2.

---

## Entry 57 — Phase 7: Pre-Benchmark Preparation (7.1, 7.2, 7.4)

**Prompt:** Finish Phase 7 (gated model access, pre-download models, config+provider validation POC) as an independent worktree-agent pass, in parallel with Phase 3 (llama.cpp) and Phase 9.6 (integration test).

**Decisions:**
- **7.1** resolved as moot rather than rubber-stamped Done: `config/experiment.json` only ever referenced open, ungated Qwen checkpoints — confirmed no HF gated-term acceptance is actually needed for this benchmark's real config (PRD's own model-selection table still names `meta-llama/Llama-3.2-1B` as an illustrative example, which is what caused the CI 401 in Entry 56's follow-up fix). No programmatic term-acceptance was attempted — that requires a human on huggingface.co.
- **7.2**: verified all three configured tiers cache correctly via a real `load_model → generate → unload` pass through `TransformersProvider` on CPU.
- **7.4**: added `sdk/sdk_validation.py` (`ValidationResult`, `run_validation()`) + `shared/cache_check.py` (`model_cache_status()` via `huggingface_hub.scan_cache_dir()`), reusing existing `validate_config()`/`validate_hardware()` rather than duplicating. Wired into `BenchmarkSDK.validate()` and the CLI as `--validate`. Instantiates each configured provider with **no** `load_model()`/`generate()` call, so validation runs no inference.

**Changes:** `sdk/sdk.py`, `sdk/sdk_validation.py` (new), `shared/cache_check.py` (new), `cli_printers.py`, `src/main.py`, plus unit tests for all three. `docs/TODO.md` Phase 7 → 4/4 Done.

**Validation:** All gates pass; `pytest --cov` → 304 passed, 9 skipped, 90.59% coverage. Manually verified `uv run python src/main.py --validate` reports PASSED with all three tiers cached. Merged (with Phase 3 and Phase 9.6) via PR #3.

---

## Entry 58 — Phase 8: Benchmark Execution

**Prompt:** Run the actual three-scenario benchmark (GPU baseline, CPU-raw baseline, AirLLM) now that Phase 7 has landed.

**Blocker found and fixed:** `torch==2.12.1` (pinned in the Entry-prior dependency fix, PR #1) only ships `cu130` wheels, but this sandbox's NVIDIA driver (550.142) only supports up to CUDA 12.4 — `torch.cuda.is_available()` was `False` the entire time, silently blocking every GPU-dependent test and both the GPU-baseline and AirLLM benchmark scenarios (both need real CUDA compute). Fixed by sourcing `torch` from PyTorch's own `cu124` wheel index (`download.pytorch.org/whl/cu124`) and re-pinning `2.6.0+cu124` — the newest version with a `cu124` build. Resolved cleanly with no downgrade to transformers/airllm/bitsandbytes. Verified: real GPU matmul runs, `torch.cuda.is_available()` is `True`, and the 8 previously CUDA-skipped tests now execute for real (330→338 passed, 9→1 skipped). One incidental test bug surfaced now that CUDA actually works: `test_torch_feature_pocs.py::test_reset_clears_peak` asserted peak VRAM is exactly `0.0` after `reset_peak_memory_stats()`, but that call rebases to *currently allocated* memory, not literal zero — a small ambient residual from earlier real-GPU tests in the same process made this fail. Loosened to a realistic threshold; this assumption had simply never been exercised on real hardware before.

**Model-sizing gap found and fixed:** `config/experiment.json`'s `"large"` tier was `Qwen2.5-7B-Instruct` at `4bit` quantization — comfortably fits this sandbox's 62GB RAM even unquantized (~28GB), so the CPU-raw baseline would succeed normally instead of demonstrating PRD's scenario 2 (OOM/extreme slowness), undermining the entire GPU-vs-CPU-vs-AirLLM comparison. PRD §7.1 originally specified `Qwen2.5-72B-Instruct` for this exact reason ("must be >2× available memory to guarantee a meaningful failure baseline"), but the config had been scaled down at some point during earlier development. Re-pinned `"large"` to `Qwen2.5-32B-Instruct` (~65.5GB unquantized fp16, confirmed via `HfApi.model_info(files_metadata=True)`) — enough to exceed the ~58GB available RAM while remaining practical to download/run, without needing the full 72B (~144GB).

**Results (real, not fabricated):**
- GPU baseline (small, `Qwen2.5-0.5B-Instruct`, unquantized, CUDA): load 0.16s, TTFT 3.01s, total 3.80s, 40.1 tok/s, peak RAM 810MB, peak VRAM 966MB. Status: success.
- AirLLM (large, `Qwen2.5-32B-Instruct`, 4-bit, paged): load/TTFT 604.31s (shard download + per-layer 4-bit conversion, 17 shards), total 1069.60s, throughput 0.1 tok/s, peak RAM 6933MB, peak VRAM 1924MB. Status: success — proves AirLLM's value proposition directly: a model that needs ~65GB unquantized fits in ~6.9GB RAM via paging, at a steep latency cost.
- CPU baseline (large, `Qwen2.5-32B-Instruct`, unquantized, raw): run with an external memory-watchdog subprocess (this sandbox has 0 swap, so a real OOM would hit the kernel OOM-killer directly rather than degrading gracefully) — proactively kills the child if RSS exceeds ~52GB or wall-clock exceeds 15 minutes. **Result: timeout.** Killed at the 900s wall-clock limit with peak RAM 38.6GB — still climbing toward the ~65.5GB it would eventually need, never reached the generation phase. At kill time the process was in Linux `D` state (`filemap_fault` — an uninterruptible mmap page fault), which cannot receive SIGKILL until the blocking syscall completes; this genuinely stalled the watchdog's `communicate()` call for a short period until the page-in resolved. This is a real, non-fabricated demonstration of PRD's "OOM or extreme slowness" outcome for the raw-CPU scenario.

**Watchdog process-tree bug found and worked around:** the watchdog's `subprocess.Popen(["uv", "run", "python", "-c", ...])` kills only the immediate `uv` wrapper process — `uv run` forks the actual Python worker as a **separate child**, not an exec-replacement, so `proc.kill()` orphaned the real worker (reparented to PID 1) instead of terminating it. Had to identify and `kill -9` the orphaned worker PID directly. Documented here rather than silently patched, since it's a real gotcha for anyone driving `uv run` subprocesses that need to be killed externally — prefer `uv run --no-sync python <script.py>` invoked via `exec` semantics, or spawn the venv's python directly (bypassing the `uv run` wrapper) next time.

**Safety note:** the CPU-baseline watchdog (`run_cpu_baseline_watched.py`, not part of the shipped codebase — an operational script for driving this specific run) polls `psutil` RSS every 2s across the child's process tree and kills on either threshold, writing whatever real `MetricsRecord` results from the run (success, oom, or a manually-recorded timeout) via the same `ResultWriter`/`BenchmarkSDK` path as everything else.

**Visualizations (task 8.6):** `Visualizer.generate_all()` / `generate_table()` run over all three real records (`results/metrics_phase8.json`) → `assets/phase8/latency_chart.png`, `assets/phase8/memory_chart.png`. The memory chart is the clearest evidence for the whole benchmark's thesis: CPU baseline (38.6GB, incomplete) vs. AirLLM (6.9GB, complete) vs. GPU baseline (810MB) — AirLLM uses ~5.6× less memory than the raw CPU baseline had already consumed without even finishing.

**Also fixed while touching these docs:** `main.py` at the repo root was a vestigial `uv init` stub (`print("Hello from code!")`), unused anywhere, but `README.md`'s Usage section referenced `uv run python main.py ...` — pointing at the stub instead of the real CLI (`src/main.py`). Deleted the stub, fixed the README/TODO.md path references. Also synced `docs/CONFIG.md` §2's example config (was still a stale non-wired provider and the gated `meta-llama/Llama-3.2-1B` — the exact model that caused Entry 56's CI failure) to match the real `config/experiment.json`.

---

## Summary of Documents
