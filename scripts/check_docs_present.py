"""Verify that all required documentation files are present.

Ported from agentic-publishing-pipeline; REQUIRED list adapted to the
AirLLM benchmark (HW5). Exits 1 with a clear message if any file is
missing.
"""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED: list[str] = [
    "README.md",
    "CLAUDE.md",
    "docs/PRD.md",
    "docs/PLAN.md",
    "docs/TODO.md",
    "docs/INTERFACES.md",
    "docs/CONFIG.md",
    "docs/IMPLEMENTATION.md",
    "config/experiment.json",
    "config/hardware.json",
    ".env-example",
    "scripts/README.md",
]


def main() -> int:
    """Report any missing required files."""
    repo_root = Path(__file__).parent.parent
    missing = [rel for rel in REQUIRED if not (repo_root / rel).exists()]

    if missing:
        print("FAIL: missing required documentation files:")
        for path in missing:
            print(f"  - {path}")
        return 1

    print(f"OK: all {len(REQUIRED)} required documentation files present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
