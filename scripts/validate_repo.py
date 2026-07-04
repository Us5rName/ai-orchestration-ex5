"""Repository validation — project-specific invariants for airllm_benchmark.

Adapted from ai-orchestration-ex4. Generic gates live in dedicated scripts
(check_line_cap, check_no_secrets, check_docs_present, check_markdown_links,
check_source_archives); this script owns only the invariants unique to the
AirLLM benchmark (HW5). No submodule required.

Checks:
  1. No personal absolute paths (/home/..., /Users/...) in committed code.
  2. Layer dependency direction: shared <- providers <- services <- sdk.
     A lower layer must never import a higher one.
  3. Config files are valid JSON with their required keys present.

A non-fatal warning is emitted when config/hardware.json still holds the
placeholder specs — real hardware must be documented before benchmarking
(PRD 6.1), but that does not block day-to-day commits.

Run: uv run python scripts/validate_repo.py
Exits 1 if any hard violation is found.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PKG = ROOT / "src" / "airllm_benchmark"
CODE_DIRS = ("src", "scripts", "tests")

_PATH = re.compile(r'["\']/(home|Users)/[A-Za-z0-9_.-]{2,}/')

# Dependency direction: each layer may not import the layers above it.
_LAYER_FORBIDS: dict[str, tuple[str, ...]] = {
    "shared": ("providers", "services", "sdk"),
    "providers": ("services", "sdk"),
    "services": ("sdk",),
}

_REQUIRED_KEYS = {
    "config/experiment.json": (
        "models", "prompts", "max_new_tokens",
        "gpu_provider", "cpu_baseline_provider",
    ),
    "config/hardware.json": ("cpu", "gpu", "ram_gb", "disk_free_gb", "os"),
}

Violations = list[str]


def _py_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, check=True, cwd=ROOT
    )
    return [
        ROOT / p for p in out.stdout.splitlines()
        if p.endswith(".py") and p.split("/", 1)[0] in CODE_DIRS
    ]


def check_personal_paths() -> Violations:
    """Check 1: no personal absolute paths in tracked code directories."""
    return [
        f"PERSONAL_PATH: {p.relative_to(ROOT)}"
        for p in _py_files()
        if p.exists() and _PATH.search(p.read_text(encoding="utf-8"))
    ]


def check_layer_isolation() -> Violations:
    """Check 2: a lower layer never imports a higher one."""
    hits: Violations = []
    for layer, forbidden in _LAYER_FORBIDS.items():
        layer_dir = PKG / layer
        if not layer_dir.exists():
            continue
        for path in layer_dir.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for upper in forbidden:
                pat = rf"(?m)^\s*(from|import)\s+airllm_benchmark\.{upper}\b"
                if re.search(pat, text):
                    rel = path.relative_to(ROOT)
                    hits.append(f"LAYER: {rel} imports airllm_benchmark.{upper}")
    return hits


def check_config_valid() -> Violations:
    """Check 3: config JSON parses and carries its required keys."""
    hits: Violations = []
    for rel, keys in _REQUIRED_KEYS.items():
        path = ROOT / rel
        if not path.exists():
            hits.append(f"CONFIG_MISSING: {rel}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            hits.append(f"CONFIG_INVALID: {rel}: {exc}")
            continue
        for key in keys:
            if key not in data:
                hits.append(f"CONFIG_KEY: {rel} missing '{key}'")
    return hits


def warn_placeholder_hardware() -> None:
    """Non-fatal: flag placeholder hardware specs (fix before benchmarking)."""
    path = ROOT / "config" / "hardware.json"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    if "placeholder" in raw.lower():
        print(
            "WARN: config/hardware.json still holds placeholder specs. "
            "Document the real machine before running benchmarks (PRD 6.1)."
        )


def main() -> int:
    """Run all hard checks; print violations; exit 1 on any failure."""
    checks = [check_personal_paths, check_layer_isolation, check_config_valid]
    violations: Violations = []
    for check in checks:
        violations.extend(check())
    warn_placeholder_hardware()
    if violations:
        print(f"FAIL: {len(violations)} violation(s)")
        for v in violations:
            print(f"  {v}")
        return 1
    print(f"OK: all {len(checks)} project-specific checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
