# AI Usage and Cost Record

| Metadata      | Value                                                        |
| ------------- | ------------------------------------------------------------ |
| **Version**   | 1.00                                                         |
| **Created**   | 2026-07-05                                                   |
| **Purpose**   | Record AI-assisted engineering and the true cost of this benchmark |
| **Scope**     | AirLLM Inference Benchmark — full repository lifecycle       |

> **Standing disclaimer.** Token counts do not by themselves establish monetary
> cost. All AI-assisted engineering on this repository ran under **plan-metered
> (subscription) billing** with no per-token charge recorded, and per-session
> token exports were **not captured**. No dollar value should be inferred without
> a verified billing model. Every measured number below traces to a file in this
> repository — nothing is retyped by hand or estimated silently.

---

## Scope

This project was built with AI assistance across its entire SDLC, following the
process fixed in [`CLAUDE.md`](../CLAUDE.md): requirements
([`docs/PRD.md`](PRD.md)) → architecture ([`docs/PLAN.md`](PLAN.md)) →
task tracking ([`docs/TODO.md`](TODO.md)) → TDD implementation → verification →
documentation.

| Attribute        | Detail                                                          |
| ---------------- | --------------------------------------------------------------- |
| **AI tool**      | Claude Code (Anthropic official CLI)                            |
| **Models**       | Claude Sonnet 5 (primary implementation), Claude Opus (review/orchestration) |
| **Billing**      | Subscription / plan-metered — **no per-token charge**           |
| **Human authors**| Lahav Tsur, Us5rName, Evyatar B.                                |
| **Decision log** | [`docs/PROMPT_LOG.md`](PROMPT_LOG.md) — 58 documented entries   |

There are **two independent cost stories** here, and they must not be conflated:

1. **Engineering AI usage** — the cost of *building* the repository (this section
   and the next). Plan-metered, not token-billed.
2. **Benchmark runtime cost** — the cost of *running* the benchmark this project
   exists to produce (measured, real, and **$0 in dollars** because every model is
   run locally). See [Benchmark Runtime Cost](#benchmark-runtime-cost-measured).

---

## Engineering AI Usage

Because sessions were plan-metered and per-token usage was not exported, this
record deliberately presents **no fabricated token table** (unlike a metered-API
project would). The honest, verifiable evidence trail is the commit history and
the prompt log.

| Metric                       | Value | Source                                  |
| ---------------------------- | ----- | --------------------------------------- |
| Commits on the project       | 127   | `git rev-list --count HEAD`             |
| Documented decision entries  | 58    | [`docs/PROMPT_LOG.md`](PROMPT_LOG.md)   |
| Commits with AI co-author trailer | 10 | `git log` (`Co-Authored-By: Claude Sonnet 5`) |
| Delivery phases / tasks      | 9 / 50 | [`docs/TODO.md`](TODO.md) §Summary      |

### Effort by phase

Phase task counts from [`docs/TODO.md`](TODO.md) §Summary — a proxy for where the
AI-assisted effort went:

| Phase | Focus                        | Tasks |
| ----- | ---------------------------- | ----- |
| 1     | Scaffolding                  | 4     |
| 2     | Configuration                | 5     |
| 3     | Providers (Transformers, llama.cpp) | 9 |
| 4     | Services (metrics, visualizer) | 5   |
| 5     | SDK (runners)                | 8     |
| 6     | CLI                          | 2     |
| 7     | Pre-benchmark preparation    | 4     |
| 8     | Benchmark execution          | 6     |
| 9     | Analysis & documentation     | 7     |
| **Total** |                          | **50** |

> **Cost status: not calculated.** Claude Code transcripts record no monetary
> cost (plan-metered); no dollar value is estimated without verified rates.

---

## Benchmark Runtime Cost (measured)

This is the cost that this project actually measures. Every model in
[`config/experiment.json`](../config/experiment.json) is an **open, ungated Qwen
checkpoint run locally** — there is **no per-token or per-API-call dollar cost**.
The real currency is **time, memory, and disk**. Numbers below are read directly
from [`results/metrics_phase8.json`](../results/metrics_phase8.json), measured on
the hardware documented in [`config/hardware.json`](../config/hardware.json).

| Scenario | Model | Load / TTFT | Total | Throughput | Peak RAM | Peak VRAM | Status | Dollar cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPU baseline | Qwen2.5-0.5B (unquantized) | 0.16s / 3.01s | 3.80s | 40.1 tok/s | 810 MB | 966 MB | ✅ success | $0 |
| AirLLM (paged, 4-bit) | Qwen2.5-32B (~65.5 GB unquantized) | 604.31s | 1069.60s | 0.1 tok/s | 6.9 GB | 1.9 GB | ✅ success | $0 |
| CPU baseline (raw) | Qwen2.5-32B (unquantized) | — never finished | 900s (killed) | — | 38.6 GB (climbing) | n/a | ⏱️ timeout | $0 |

**Workload per scenario:** one prompt, `max_new_tokens = 32`
([`config/experiment.json`](../config/experiment.json)).

The AirLLM row is the whole point: a model needing **~65.5 GB unquantized** runs
in **~6.9 GB RAM** via paged inference — at the cost of ~18 minutes for one short
answer. The CPU-baseline row is the "OOM or extreme slowness" outcome the
raw-CPU scenario is designed to produce (see [`docs/TODO.md`](TODO.md) task 8.3).
None of these consumed a paid API quota.

---

## Illustrative List-Price Cost (hypothetical — NOT billed)

The benchmark's inference workload is tiny — three prompts, 32 output tokens
each. **If** that same workload were routed through a paid hosted API instead of
run locally, the order of magnitude would be:

- Input: ~3 prompts × ~15 tokens ≈ **45 input tokens**
- Output: 3 × 32 = **96 output tokens**

Even at premium frontier-model list prices (~$3–$15 / M input, ~$15–$75 / M
output), that is a **fraction of one cent** — far below the granularity of any
real invoice. This illustrates the point rather than establishing a charge:
**it was never billed.** The local run's actual cost is the compute time and
memory in the table above, not dollars.

---

## Cost Calculation Template

Should anyone re-run this workload under a **verified** paid billing model, a
dollar figure can be computed as:

```
ordinary_input_cost = non_cached_input_tokens / 1_000_000 × ordinary_input_rate
cached_input_cost   = cached_input_tokens     / 1_000_000 × cached_input_rate
output_cost         = output_tokens           / 1_000_000 × output_rate
estimated_total_cost = ordinary_input_cost + cached_input_cost + output_cost
```

Rates must come from the provider's published pricing at time of use. This
template is provided for completeness only; **no rates are asserted here.**

---

## Efficiency Observations

Process improvements captured during development (from
[`docs/PROMPT_LOG.md`](PROMPT_LOG.md)) — qualitative, not measured savings:

- **Reuse over duplication.** Pre-benchmark validation (`--validate`) reused the
  existing `validate_config()` / `validate_hardware()` helpers in
  `shared/config_loader.py` rather than re-implementing them (task 7.4).
- **No fabricated numbers.** Every figure in the analysis notebook and these docs
  is computed from `results/metrics_phase8.json`, not retyped — eliminating a
  whole class of drift between prose and data.
- **Fail fast, cheaply.** `--validate` runs a full config/provider/HF-cache dry
  run with **no inference**, catching misconfiguration before the expensive
  multi-minute benchmark runs (task 7.4).
- **Operational gotcha logged, not hidden.** `uv run` forks the real Python worker
  as a separate child, so killing the wrapper orphans it — the CPU-baseline
  watchdog had to target the worker PID directly (Entry 58). Documented for reuse.

---

## Provenance

| Datum | Source of truth |
| --- | --- |
| Benchmark timings, memory, status | [`results/metrics_phase8.json`](../results/metrics_phase8.json) |
| Commit / author counts | `git rev-list`, `git shortlog`, `git log` |
| Decision entries, effort narrative | [`docs/PROMPT_LOG.md`](PROMPT_LOG.md) |
| Phase / task totals | [`docs/TODO.md`](TODO.md) §Summary |
| Models, prompts, token budget | [`config/experiment.json`](../config/experiment.json) |
| Benchmark hardware | [`config/hardware.json`](../config/hardware.json) |

No token or dollar figure in this document was invented; where a value could not
be measured (per-session tokens), that is stated plainly rather than estimated.
