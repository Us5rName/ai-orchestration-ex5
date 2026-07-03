# Implementation Instructions

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.01                                   |
| **Based on**  | `docs/INTERFACES.md` v1.00             |

> Every module is built through progressive proof-of-concepts before the final implementation. This ensures correctness, testability, and confidence in external dependencies.

---

## ⚠️ Pre-Implementation Gate

**Before starting any implementation step, verify:**

1. **Check `docs/INTERFACES.md`** — Does the module's interface exist and is it clear?
2. **If the interface is missing, ambiguous, or incomplete** — **STOP.** Do not design or implement anything.
3. **Notify the user.** Clearly state what is missing and wait for approval before proceeding.
4. **Only continue** after the user has resolved the gap (by updating INTERFACES.md or providing explicit direction).

> **No implementation before user approves.** This applies to all gaps: missing interfaces, unclear requirements, ambiguous specs, or anything that requires a design decision beyond what's documented.

---

## Module Implementation Process

Each module follows a three-step process:

### Step 1 — Library PoC

Write a minimal, standalone proof-of-concept for each external library needed that proves you know how to load and use the external libraries needed.

- **Goal:** Verify the library is available, importable, and functional.
- **Scope:** The smallest possible script that exercises the core functionality (e.g., load a model, generate one sentence).
- **Testing:** Must include a test that runs the PoC and asserts it produces valid output. **Always test against real data** — run the PoC on the actual machine with real resources (e.g. real network, real filesystem, real hardware); the point is to confirm the library works in the target environment.

### Step 2 — Feature PoCs

Write a separate PoC for **every feature** that will be exposed through the module's public interface (as defined in `docs/INTERFACES.md`).

- **Goal:** Prove each interface method can be implemented correctly before writing the module.
- **Scope:** One PoC per interface method or feature. Each PoC isolates a single concern.
- **Testing:** Every PoC must be tested. Tests assert the PoC produces the expected output for its feature. **Always test against real data** — exercise the actual library with real resources (e.g. real model loads, real API calls, real file I/O).

### Step 3 — Full Module

Using the **actual code** from the PoCs as the foundation, build the complete module.

- **Goal:** Deliver a production-quality module that satisfies its interface contract.
- **Scope:** Reuse PoC code directly — add error handling, input validation, docstrings, and test coverage on top of the proven PoC patterns. Do not rewrite from scratch.
- **Testing:** Unit tests for the module, all external dependencies mocked per project rules.

---

## Example: Ollama Provider

| Step | PoC | Test |
|------|-----|------|
| 1 — Library PoC | Import `ollama`, call `ollama.generate()`, print output | Assert output is non-empty string |
| 2 — Feature PoC: `load_model` | Pull model via `ollama.pull()`, verify model exists locally | Assert model is available |
| 2 — Feature PoC: `generate` | Call `ollama.generate()` with `options.num_predict`, assert token limit | Assert output ≤ `max_tokens` |
| 2 — Feature PoC: `unload` | Verify no explicit unload needed (HTTP-based, stateless) | Assert no side effects |
| 3 — Full Module | Implement `OllamaProvider` class with all three methods | Mock HTTP; test protocol compliance |

---

## Mandatory Standards

Every step (PoC and final module) must obey the project rules from [`CLAUDE.md`](../CLAUDE.md). These are **in addition** to the PoC process above — not optional.

| Rule | Requirement | Reference |
|------|-------------|-----------|
| **TDD** | RED → GREEN → REFACTOR. Tests written alongside code. | `CLAUDE.md` §5 |
| **150-Line Limit** | No file exceeds 150 lines. Split using helpers or module separation. | `CLAUDE.md` §4 |
| **Zero Ruff** | `ruff check` must return 0 violations. | `CLAUDE.md` §4 |
| **No Hardcoding** | All config in `config/*.json` or `.env`. Only physical constants in code. | `CLAUDE.md` §4 |
| **Docstrings** | Every module, class, and function gets a detailed docstring. | `CLAUDE.md` §4 |
| **Comments** | Explain "Why," not "What." | `CLAUDE.md` §4 |
| **Mocking** | All external dependencies mocked in unit tests (Ollama, HF Hub, psutil). | `CLAUDE.md` §5 |
| **Coverage** | ≥ 85% global coverage (statement, branch, critical path). | `CLAUDE.md` §5 |
| **uv Only** | All dependency management via `uv run`. No `pip`, `venv`, `virtualenv`. | `CLAUDE.md` §6 |
| **SDK-First** | All business logic flows through `sdk/sdk.py`. CLI delegates to SDK. | `CLAUDE.md` §3 |
| **Gatekeeper** | All external API calls flow through `shared/gatekeeper.py`. | `CLAUDE.md` §3 |
| **DRY** | Extract shared logic if it appears 2+ times. | `CLAUDE.md` §4 |
| **Modular Design** | Single responsibility, separation of concerns, testable in isolation. | `modular-design` skill |
| **Interfaces Are Holy** | Never modify `docs/INTERFACES.md` without user consultation. | `CLAUDE.md` §1 |

---

## PoC Rules

- **No PoC, no module.** Do not skip PoCs. They are the foundation of correct implementation.
- **Every PoC is tested.** An untested PoC provides no confidence.
- **PoCs always use real data.** Steps 1 and 2 (Library PoC + Feature PoCs) exercise the actual library against its real environment — real network, real filesystem, real hardware. This proves the library works before the module abstracts it away.
- **PoCs inform implementation.** Use PoC results to design error handling, edge cases, and timeouts in the final module.
- **PoC code is reused.** The actual code from PoCs becomes the foundation of the final module. Do not rewrite from scratch — adapt the proven PoC patterns by adding error handling, validation, and docstrings. The PoC files themselves are disposable and can be removed after the module is complete.

---

## Implementation Checklist

Before marking a module as complete, verify:

- [ ] Library PoC executed and tested
- [ ] Feature PoCs executed and tested for every interface method
- [ ] Full module implements interface contract from `docs/INTERFACES.md`
- [ ] All mandatory standards above satisfied (TDD, ruff=0, 150-line limit, etc.)
- [ ] Unit tests pass with external dependencies mocked
- [ ] Docstrings present on all public APIs
- [ ] No hardcoded values — config externalized
- [ ] `uv run ruff check` returns 0 violations
- [ ] Relevant integration checkpoint passes (see `docs/TODO.md`)
