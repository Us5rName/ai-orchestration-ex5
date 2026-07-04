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
- Includes concrete example for Ollama Provider

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
- Includes concrete example for Ollama Provider

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

**Context:** User changed plan to use transformers as GPU provider instead of ollama. The `transformers_provider.py` already existed from Phase 3 (Step 1-3 per IMPLEMENTATION.md). PoCs existed and were tested.

**Decisions:**
- Updated `config/experiment.json` to use `gpu_provider: "transformers"` with `device: "cuda"`
- Removed ollama provider from plan (no longer needed as transformers serves both GPU and CPU)
- Updated `docs/TODO.md` to reflect plan change
- Fixed bug: tokenizer inputs were on CPU while model was on CUDA → added `.to(self._device)` in `generate()`
- Added real device tests (`tests/unit/test_transformers_device.py`) for both CPU and GPU paths

**Changes:**
- `config/experiment.json` — gpu_provider → transformers, device → cuda
- `src/airllm_benchmark/providers/transformers_provider.py` — fixed device mismatch bug
- `docs/TODO.md` — marked ollama removed, added GPU/CPU verification tasks
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

**Context:** TODO item 3.6 (`tests/unit/test_providers.py`) was the only unimplemented task in Phase 3 besides the llama.cpp provider (3.5). The Ollama provider (3.3) was already removed.

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

## Entry 34 — INCONSISTENCIES.md: Ollama References After GPU Provider Change

**Prompt:** "Look at the prompt log, you will see that the gpu provider was changed to transformers. Please update inconcistensies.md" → "And update the version and add to the prompt log and commit"

**Context:** Per Entry 22, the GPU provider was changed from ollama to transformers. `config/experiment.json` was updated, `ollama_provider.py` was removed, and TODO.md was updated. However, multiple documentation files still reference ollama as if it were an active provider.

**Decisions:**
- Added new inconsistency (#2) to `docs/INCONSISTENCIES.md` tracking all ollama references across 6 documents
- Bumped version from 1.01 to 1.02
- Documents affected: `CLAUDE.md`, `docs/CONFIG.md`, `docs/INTERFACES.md`, `docs/PLAN.md`, `docs/IMPLEMENTATION.md`

**Changes:**
- `docs/INCONSISTENCIES.md` — Added Entry #2: Ollama References (v1.02)
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

## Summary of Documents
