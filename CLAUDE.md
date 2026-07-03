# AirLLM Inference Benchmark — Project Rules

AI Orchestration Course — Exercise 5. Version 1.00.

## Project Context

This project benchmarks LLM inference across three memory scenarios:
- **Small model on GPU** — fast baseline (model fits in VRAM)
- **Large model on CPU (raw)** — OOM or extreme slowness (model exceeds memory)
- **Large model via AirLLM** — succeeds with latency trade-off (paged inference)

The key distinction is whether the model fits in available memory — not which provider is used. Providers (Ollama, Transformers, llama.cpp) are configurable and support both GPU and CPU targets.

## Mandatory Documents

All documents must be read before implementation. They define the contract.

| Document | Purpose |
|----------|----------|
| [`docs/PRD.md`](docs/PRD.md) | Requirements, goals, experiment design |
| [`docs/PLAN.md`](docs/PLAN.md) | C4 architecture, ADRs, data flow |
| [`docs/CONFIG.md`](docs/CONFIG.md) | Config schemas (experiment.json, hardware.json, metrics) |
| [`docs/INTERFACES.md`](docs/INTERFACES.md) | SDK API, InferenceProvider, InferenceRunner contracts |
| [`docs/TODO.md`](docs/TODO.md) | Task tracking, integration plan, checkpoints |

## 1. Core Philosophy
- **Plan Before Execution**: Never write code before PRD, PLAN, and TODO are approved.
- **Uncompromising Quality**: Clean code, full documentation, comprehensive test coverage.
- **Broad Thinking**: Understand the full benchmark lifecycle, not just the immediate function.
- **Transparency**: Document the "why" behind technical decisions. Maintain prompt log.
- **Interfaces Are Holy**: `docs/INTERFACES.md` defines the immutable contract between components. Never modify interfaces without explicit consultation with the user. All implementation decisions must respect and adhere to the published interfaces.

## 2. Mandatory SDLC
1. **Requirements**: `docs/PRD.md` — goals, KPIs, acceptance criteria.
2. **Architecture**: `docs/PLAN.md` — C4 models, ADRs.
3. **Task Tracking**: `docs/TODO.md` — prioritized tasks, integration plan.
4. **Implementation (TDD)**: RED → GREEN → REFACTOR. Tests alongside each phase.
5. **Verification**: Tests, coverage ≥ 85%, ruff = 0, final checklist.
6. **Documentation**: `README.md`, analysis notebook.

## 3. Technical Architecture

### Package Layout
```
src/airllm_benchmark/
├── sdk/                          # SDK layer (single entry point)
│   ├── sdk.py                    # BenchmarkSDK entry point
│   ├── runner.py                 # Runner manager + InferenceRunner protocol
│   ├── gpu_runner.py             # GPU runner (delegates to provider)
│   ├── cpu_runner.py             # CPU baseline runner (delegates to provider)
│   └── airllm_runner.py          # AirLLM paged runner (builtin)
├── providers/                    # Providers layer (facade pattern)
│   ├── base.py                   # InferenceProvider protocol
│   ├── ollama_provider.py        # Ollama HTTP client
│   ├── transformers_provider.py  # HuggingFace Transformers wrapper
│   └── llamacpp_provider.py      # llama.cpp Python bindings
├── services/                     # Supporting services
│   ├── metrics.py                # Timing + psutil memory sampling
│   └── visualizer.py             # Chart + table generation
├── shared/                       # Shared utilities
│   ├── config.py                 # Config loader (JSON + .env)
│   └── version.py                # Version tracking (1.00)
└── constants.py                  # Enums, physical constants
```

### SDK-First Design
- **Single Entry Point**: All logic flows through `sdk/sdk.py` (`BenchmarkSDK`).
- **Delegation**: CLI (`src/main.py`) delegates all logic to SDK.
- **No Leakage**: No external consumer imports internal services directly.

### Providers Layer
- All providers implement `InferenceProvider` protocol (`providers/base.py`).
- Runners delegate to a configured provider (facade pattern).
- Both GPU and CPU baseline runners are provider-configurable via `config/experiment.json`.
- AirLLM has its own runner (builtin, no provider — uses paged inference).

### API Gatekeeper
- All external API calls (Ollama HTTP, HuggingFace downloads) flow through `shared/gatekeeper.py`.
- Rate limiting enforced from `config/rate_limits.json`.
- FIFO queue for overflow; never crash due to rate limits.

## 4. Strict Coding Standards
- **150-Line Limit**: No file exceeds 150 lines. Split using helpers, extraction, or module separation.
- **Zero-Ruff Policy**: `ruff check` must return 0 violations.
- **No Hardcoding**: All config in `config/*.json` or `.env`. Only physical constants in code.
- **DRY**: Extract shared logic if it appears 2+ times.
- **Docstrings**: Every module, class, function gets a detailed docstring.
- **Comments**: Explain "Why," not "What."
- **Naming**: Descriptive, precise names that convey intent.

## 5. Quality Assurance & Testing
- **TDD**: Tests written alongside each phase (see `docs/TODO.md` integration plan).
- **Coverage**: ≥ 85% global coverage (statement, branch, critical path).
- **Mocking**: All external dependencies mocked in unit tests (Ollama, HF Hub, psutil).
- **Integration**: Staged bottom-up integration (I1–I15). Checkpoints CP1–CP12.

## 6. Tooling & Infrastructure
- **Package Management**: `uv` only. No `pip`, `venv`, `virtualenv`.
- **Command Style**: Always `uv run <command>`.
- **Versioning**: `1.00` in `src/airllm_benchmark/shared/version.py`.
- **Prompt Log**: `docs/PROMPT_LOG.md` — prompts, context, decisions, improvements.
- **Git**: Meaningful commits, feature branches.

## 7. Research & Analysis
- **Analysis Notebook**: `notebooks/analysis.ipynb` — results analysis with LaTeX formulas.
- **Visualization**: High-resolution charts in `assets/` (Bar, Line, Scatter, Heatmap).
- **Cost Tracking**: Input/output tokens, cost breakdown per model.

## 8. Final Verification Checklist
- [ ] All logic flows through SDK (`sdk/sdk.py`).
- [ ] All external API calls flow through Gatekeeper (`shared/gatekeeper.py`).
- [ ] `ruff check` = 0 violations.
- [ ] Test coverage ≥ 85%.
- [ ] No file > 150 lines.
- [ ] No hardcoded secrets or config.
- [ ] Mandatory docs (`PRD`, `PLAN`, `TODO`, `CONFIG`, `INTERFACES`) up to date.
- [ ] `uv` used for all dependency management.
- [ ] All integration checkpoints (CP1–CP12) pass.
- [ ] Hardware specs documented in `config/hardware.json`.
