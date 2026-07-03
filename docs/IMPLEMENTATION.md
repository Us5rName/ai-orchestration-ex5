# Implementation Instructions

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.00                                   |
| **Based on**  | `docs/INTERFACES.md` v1.00             |

> Every module is built through progressive proof-of-concepts before the final implementation. This ensures correctness, testability, and confidence in external dependencies.

---

## Module Implementation Process

Each module follows a three-step process:

### Step 1 — Library PoC

Write a minimal, standalone proof-of-concept that proves you know how to load and use the external library.

- **Goal:** Verify the library is available, importable, and functional.
- **Scope:** The smallest possible script that exercises the core functionality (e.g., load a model, generate one sentence).
- **Testing:** Must include a test that runs the PoC and asserts it produces valid output.

### Step 2 — Feature PoCs

Write a separate PoC for **every feature** that will be exposed through the module's public interface (as defined in `docs/INTERFACES.md`).

- **Goal:** Prove each interface method can be implemented correctly before writing the module.
- **Scope:** One PoC per interface method or feature. Each PoC isolates a single concern.
- **Testing:** Every PoC must be tested. Tests assert the PoC produces the expected output for its feature.

### Step 3 — Full Module

Using the lessons learned from the PoCs, build the complete module.

- **Goal:** Deliver a production-quality module that satisfies its interface contract.
- **Scope:** Full implementation with error handling, input validation, docstrings, and test coverage.
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

## Rules

- **No PoC, no module.** Do not skip PoCs. They are the foundation of correct implementation.
- **Every PoC is tested.** An untested PoC provides no confidence.
- **PoCs inform implementation.** Use PoC results to design error handling, edge cases, and timeouts in the final module.
- **PoCs are disposable.** They do not need to survive in the codebase after the module is complete. Their purpose is learning and validation.
