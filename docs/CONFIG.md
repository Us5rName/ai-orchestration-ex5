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
| `provider`         | string   | Provider name (e.g., `"ollama"`, `"transformers"`) |
| `prompt`           | string   | Input prompt text                              |
| `prompt_id`        | string   | Prompt identifier (P1, P2, P3)                 |
| `quantization`     | string   | `"4bit"`, `"8bit"`, or `"none"`                |
| `max_new_tokens`   | integer  | Token generation limit                         |
| `load_time_s`      | float    | Seconds to load model into memory              |
| `ttft_s`           | float    | Time to first token (seconds)                  |
| `total_runtime_s`  | float    | Total inference time (seconds)                 |
| `tokens_generated` | integer  | Number of tokens produced                      |
| `generation_throughput` | float | Tokens per second during generation phase      |
| `peak_ram_mb`      | float    | Peak RAM usage during inference (MB)           |
| `peak_vram_mb`     | float    | Peak VRAM usage during inference (MB, if GPU)  |
| `status`           | string   | `"success"`, `"oom"`, `"timeout"`              |
| `error`            | string   | Error message if status != `"success"`         |
| `timestamp`        | string   | ISO 8601 timestamp of run                      |

---

## 2. Experiment Configuration — `config/experiment.json`

```json
{
  "models": {
    "small": { "id": "meta-llama/Llama-3.2-1B", "tier": "small" },
    "medium": { "id": "Qwen/Qwen2.5-7B-Instruct", "tier": "medium" },
    "large": { "id": "Qwen/Qwen2.5-72B-Instruct", "tier": "large" }
  },
  "prompts": {
    "P1": "What is the capital of the United States?",
    "P2": "Explain quantum entanglement in one paragraph.",
    "P3": "Write a Python function that sorts a list."
  },
  "max_new_tokens": 32,
  "quantization": "4bit",
  "gpu_provider": "ollama",
  "cpu_baseline_provider": "transformers",
  "provider_config": {
    "ollama": { "base_url": "http://localhost:11434" },
    "transformers": { "device": "cpu" }
  }
}
```

### Fields

| Field                   | Type   | Description                                        |
| ----------------------- | ------ | -------------------------------------------------- |
| `models`                | object | Named model tiers with HF IDs                      |
| `prompts`               | object | Named test prompts                                 |
| `max_new_tokens`        | int    | Token generation limit for all runs                |
| `quantization`          | string | Quantization level for AirLLM (`"4bit"` / `"8bit"`) |
| `gpu_provider`          | string | Provider for GPU baseline (e.g., `"ollama"`)       |
| `cpu_baseline_provider` | string | Provider for CPU baseline (e.g., `"transformers"`) |
| `provider_config`       | object | Per-provider settings                              |

---

## 3. Hardware Configuration — `config/hardware.json`

```json
{
  "cpu": "",
  "gpu": "",
  "ram_gb": 0,
  "disk_free_gb": 0,
  "os": "",
  "documented_by": "",
  "documented_at": ""
}
```

> All fields must be filled before running benchmarks. Empty values cause the SDK to abort with a clear error.

### Fields

| Field            | Type    | Description                           |
| ---------------- | ------- | ------------------------------------- |
| `cpu`            | string  | CPU model name                        |
| `gpu`            | string  | GPU model name + VRAM                 |
| `ram_gb`         | number  | Total system RAM (GB)                 |
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
