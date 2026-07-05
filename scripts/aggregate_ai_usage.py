#!/usr/bin/env python3
"""Aggregate real Claude Code session usage from local JSONL transcripts.

Scans ~/.claude/projects/-root-ai-orchestration-ex5/ for *.jsonl and
subagents/*.jsonl files, extracts per-model token counts and message
cardinality from the 'usage' block in each assistant message, and prints
a Markdown table for documentation. No prompt content, file paths, or
request IDs are emitted — only aggregated counts.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def aggregate_sessions():
    """Scan JSONL transcripts and aggregate per-model token/message counts.

    Returns:
        dict: {
            'models': {model: {'input': ..., 'output': ..., ...}},
            'sessions': set of session UUIDs,
            'time_range': (min_ts, max_ts)
        }
    """
    project_dir = Path.home() / ".claude" / "projects" / "-root-ai-orchestration-ex5"
    if not project_dir.exists():
        print(f"Error: {project_dir} not found.", file=sys.stderr)
        sys.exit(1)

    # Find all JSONL files: top-level and in subagents/ subdirs.
    jsonl_files = list(project_dir.glob("*.jsonl")) + list(
        project_dir.glob("*/subagents/*.jsonl")
    )
    if not jsonl_files:
        print(f"Error: no JSONL files found under {project_dir}", file=sys.stderr)
        sys.exit(1)

    agg = defaultdict(lambda: defaultdict(int))
    sessions = set()
    timestamps = []

    for fpath in jsonl_files:
        try:
            with open(fpath) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Track session UUID.
                    sid = entry.get("sessionId")
                    if sid:
                        sessions.add(sid)

                    # Track timestamp for date range.
                    ts = entry.get("timestamp")
                    if ts:
                        timestamps.append(ts)

                    # Extract usage from message.
                    msg = entry.get("message")
                    if not isinstance(msg, dict):
                        continue

                    model = msg.get("model")
                    usage = msg.get("usage")
                    if not model or not usage:
                        continue

                    # Skip synthetic entries (zero real usage).
                    if model == "<synthetic>":
                        continue

                    # Accumulate per-model token counts.
                    m = agg[model]
                    m["input"] += usage.get("input_tokens", 0)
                    m["output"] += usage.get("output_tokens", 0)
                    m["cache_creation"] += usage.get(
                        "cache_creation_input_tokens", 0
                    )
                    m["cache_read"] += usage.get("cache_read_input_tokens", 0)
                    m["messages"] += 1

        except OSError as e:
            print(f"Warning: could not read {fpath}: {e}", file=sys.stderr)
            continue

    time_min = min(timestamps) if timestamps else None
    time_max = max(timestamps) if timestamps else None

    return {
        "models": dict(agg),
        "sessions": sessions,
        "time_range": (time_min, time_max),
    }


def print_table(data):
    """Print Markdown table and metadata."""
    models = data["models"]
    sessions = data["sessions"]
    time_min, time_max = data["time_range"]

    # Print metadata.
    print(f"**Sessions (top-level + subagent):** {len(sessions)}")
    print(f"**Date range:** {time_min} → {time_max}\n")

    # Print header.
    print(
        "| Model | Messages | Input Tokens | Output Tokens | "
        "Cache Creation | Cache Read |"
    )
    print("|-------|----------|--------------|---------------|-----------|-----------|")

    # Print per-model rows.
    totals = defaultdict(int)
    for model in sorted(models.keys()):
        m = models[model]
        for key in ["input", "output", "cache_creation", "cache_read", "messages"]:
            totals[key] += m.get(key, 0)

        print(
            f"| {model} | {m['messages']} | {m['input']:,} | {m['output']:,} | "
            f"{m['cache_creation']:,} | {m['cache_read']:,} |"
        )

    # Print totals row.
    print(
        f"| **TOTAL** | {totals['messages']} | {totals['input']:,} | "
        f"{totals['output']:,} | {totals['cache_creation']:,} | "
        f"{totals['cache_read']:,} |"
    )


if __name__ == "__main__":
    data = aggregate_sessions()
    print_table(data)
