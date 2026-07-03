# Lesson: Interface-First Design — Metrics Service Discovery

| Metadata  | Value                            |
| --------- | -------------------------------- |
| **Date**  | 2026-07-03                       |
| **Phase** | 4.1 — Services (Metrics)         |
| **Status** | Lesson Learned                  |

---

## What Happened

Started implementing `services/metrics.py` (Phase 4.1) following the IMPLEMENTATION.md PoC process. Designed a `MetricsCollector` API with methods: `start()`, `stop_sampling()`, `get_record()`.

Then discovered: **`docs/INTERFACES.md` does not define an interface for the metrics service.**

INTERFACES.md defines contracts for:
- `BenchmarkSDK` (SDK entry point)
- `InferenceProvider` (providers layer)
- `InferenceRunner` (runners layer)

But **not** for internal services like `metrics.py` or `visualizer.py`.

## The Problem

**Two failures occurred:**

### 1. Missing Contract (Design Problem)

Designed a public API without a contract to follow. This means:

1. **No guarantee of fit** — The API might not match how runners actually consume metrics
2. **Risk of rework** — If runners need different methods, the entire module may need refactoring
3. **Violation of "Interfaces Are Holy"** — Even though INTERFACES.md doesn't cover this, the principle still applies: design the interface before implementation

### 2. No Notification (Process Problem)

Discovered the missing contract but **continued designing and implementing anyway**. This is the critical failure.

The correct process is:

1. **Discover** the gap (missing interface, unclear requirement, ambiguous spec)
2. **Stop** — do not proceed with implementation
3. **Notify the user** — clearly state the problem and ask for guidance
4. **Wait for approval** — only continue after the user decides how to resolve it

**No implementation before user approves.** This is non-negotiable.

## What to Do

### 1. Derive the Interface from Consumers

The metrics service is consumed by runners (`gpu_runner`, `cpu_runner`, `airllm_runner`). Design the interface by answering:

> **What does a runner need from metrics during a benchmark run?**

The runner lifecycle is:
```
load model → generate text → collect metrics → return metrics dict
```

So the interface must support:
- Timing operations (start, checkpoint, stop)
- Memory sampling during operations
- Assembling a metrics record matching CONFIG.md §1 schema

### 2. Define the Contract First

Before writing `metrics.py`, define the interface in `docs/INTERFACES.md` or as a Protocol in `services/base.py`:

```python
class MetricsCollector(Protocol):
    """Interface for metrics collection during inference."""

    def start(self) -> None: ...
    def snapshot_load_time(self) -> float: ...
    def stop(self) -> None: ...
    def get_record(self, ...) -> dict: ...
```

### 3. Then Implement

Only after the interface is defined should the full module be built. The PoCs already prove the features work — they just need to be adapted to the correct interface.

## General Rule

> **Always check INTERFACES.md before designing a module's public API.** If the interface is missing, define it first. Never design implementation details before the contract.

## Action Items

- [ ] Define `MetricsCollector` interface in `docs/INTERFACES.md` or `services/base.py`
- [ ] Verify interface matches runner consumption patterns
- [ ] Rebuild `metrics.py` against the defined interface
- [ ] Same check for `visualizer.py` before implementing Phase 4.4
