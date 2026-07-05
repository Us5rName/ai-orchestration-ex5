# Configuration Contract

| Metadata      | Value                                  |
| ------------- | -------------------------------------- |
| **Version**   | 1.00                                   |
| **Based on**  | `docs/PRD.md` v1.00, `docs/PLAN.md` v1.00 |

---

## 1. Metrics Record — `results/metrics.json`

Each inference run produces one record appended to the JSON array.

| Field              | Type     | Description                                    |
| ------------------ | -------- | ---------------------------------------------- |
| `run_id`           | string   | Unique identifier (e.g., `run_001`)            |
| `model`            | string   | HuggingFace model identifier                   |
| `mode`             | string   | `"gpu_provider"`, `"cpu_baseline"`, `"airllm"`  |
| `provider`         | string   | Provider name (e.g., `"transformers"`, `"llamacpp"`) |
| `prompt`           | string   | Input prompt text                              |
| `prompt_id`        | string   | Prompt identifier (P1, P2, P3)                 |
| `quantization`     | string   | `"4bit"`, `"8bit"`, or `"none"`                |
| `max_new_tokens`   | integer  | Token generation limit                         |
| `load_time_s`      | float    | Seconds to download + load model (setup time)  |
| `ttft_s`           | float    | Real time-to-first-token, from generation start to the first token produced (seconds). `0.0` when the provider does not support per-token measurement (see INTERFACES.md metrics section) — never approximated from load/setup time. |
| `total_runtime_s`  | float    | Total inference time (seconds)                 |
| `tokens_generated` | integer  | Number of tokens produced                      |
| `generation_throughput` | float | Tokens per second during generation phase      |
| `peak_ram_mb`      | float    | Peak RAM usage during inference (MB)           |
| `peak_vram_mb`     | float    | Peak VRAM usage during inference (MB, if GPU)  |
| `status`           | string   | `"success"`, `"oom"`, `"timeout"`              |
| `error`            | string   | Error message if status != `"success"`         |
| `timestamp`        | string   | ISO 8601 timestamp of run                      |

`assets/metrics.csv` (written by `services/report_tables.export_metrics_csv`,
per docs/INTERFACES.md §11) mirrors this schema exactly, plus one derived
column: `tier` (`"small"`/`"medium"`/`"large"`/`"unknown"`, resolved from
`config/experiment.json`). No schema change to `MetricsRecord` itself.

---

## 2. Experiment Configuration — `config/experiment.json`

```json
{
  "models": {
    "small": { "id": "Qwen/Qwen2.5-0.5B-Instruct", "tier": "small" },
    "medium": { "id": "Qwen/Qwen2.5-3B-Instruct", "tier": "medium" },
    "large": { "id": "Qwen/Qwen2.5-32B-Instruct", "tier": "large" }
  },
  "prompts": {
    "P1": "What is the capital of the United States?",
    "P2": "Explain quantum entanglement in one paragraph.",
    "P3": "Write a Python function that sorts a list."
  },
  "max_new_tokens": 32,
  "quantization": "4bit",
  "gpu_provider": "transformers",
  "cpu_baseline_provider": "transformers",
  "provider_config": {
    "transformers": { "device": "cuda" }
  }
}
```

> All models are open, ungated Qwen checkpoints — no HuggingFace token or gated-term acceptance is required. `gpu_provider`/`cpu_baseline_provider` are both `"transformers"`. The `"large"` tier must exceed available system RAM unquantized to demonstrate the CPU-raw-baseline failure/slowness scenario (see `docs/PRD.md` §7.1's Selection Rule).

### Fields

| Field                   | Type   | Description                                        |
| ----------------------- | ------ | -------------------------------------------------- |
| `models`                | object | Named model tiers with HF IDs                      |
| `prompts`               | object | Named test prompts                                 |
| `max_new_tokens`        | int    | Token generation limit for all runs                |
| `quantization`          | string | Quantization level for AirLLM (`"4bit"` / `"8bit"`) |
| `gpu_provider`          | string | Provider for GPU baseline (e.g., `"transformers"`) |
| `cpu_baseline_provider` | string | Provider for CPU baseline (e.g., `"transformers"`) |
| `provider_config`       | object | Per-provider settings (see below)                  |

### Provider Configuration

The `provider_config` object contains settings for each available provider.

**Transformers provider:**
```json
"transformers": {
  "device": "cuda"
}
```
- `device` (string): Target device — `"cuda"` for GPU, `"cpu"` for CPU.

**llama.cpp provider (optional):**
```json
"llamacpp": {
  "device": "cuda"
}
```
- `device` (string): Target device — `"cuda"` for GPU (uses `n_gpu_layers` internally), `"cpu"` for CPU-only.

To select a provider for GPU or CPU baseline, set `gpu_provider` or `cpu_baseline_provider` to its name (e.g., `"llamacpp"`). Model identifiers can be local paths (`"/path/to/model.gguf"`) or HuggingFace Hub identifiers in the form `"repo_id::filename"`.

---

## 3. Hardware Configuration — `config/hardware.json`

```json
{
  "cpu": "",
  "gpu": "",
  "ram_gb": 0,
  "vram_gb": 0,
  "disk_free_gb": 0,
  "os": "",
  "documented_by": "",
  "documented_at": ""
}
```

> All fields must be filled before running benchmarks. Empty/zero values cause the SDK to abort with a clear error.

### Fields

| Field            | Type    | Description                           |
| ---------------- | ------- | ------------------------------------- |
| `cpu`            | string  | CPU model name                        |
| `gpu`            | string  | GPU model name + VRAM                 |
| `ram_gb`         | number  | Total system RAM (GB)                 |
| `vram_gb`        | number  | Total GPU VRAM (GB) — reference line for the V2b VRAM chart (`report_charts.py::render_vram_by_tier_chart`) |
| `disk_free_gb`   | number  | Free disk space (GB)                  |
| `os`             | string  | Operating system + version            |
| `documented_by`  | string  | Who documented the specs              |
| `documented_at`  | string  | ISO 8601 timestamp of documentation   |

---

## 4. Environment Variables — `.env`

| Variable     | Description                    | Required |
| ------------ | ------------------------------ | -------- |
| `HF_TOKEN`   | HuggingFace API token          | Yes*     |

> *Required only for gated models (e.g., Llama). Open models (Qwen) do not need a token.

---

## 5. Rate Limits — `config/rate_limits.json`

Read by the API Gatekeeper (`shared/gatekeeper.py`, see `INTERFACES.md` §9) to
pace external calls. A missing file or missing service key disables limiting
for that service — the gatekeeper never crashes due to a config gap.

```json
{
  "huggingface": { "calls_per_minute": 30 }
}
```

### Fields

| Field                        | Type   | Description                                  |
| ---------------------------- | ------ | --------------------------------------------- |
| `<service>`                  | object | Rate-limit bucket, keyed by service name       |
| `<service>.calls_per_minute` | int    | Max calls/minute; `<= 0` or absent disables limiting |
