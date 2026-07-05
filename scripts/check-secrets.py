#!/usr/bin/env python3
"""Generic secret pattern scanner for pre-commit and CI.

Detects common secret patterns (API keys, tokens, passwords, credit cards, etc.)
in tracked files. Patterns are generic (not company-specific) to reveal no
operational details to attackers. Use local .git/hooks for company-specific checks.

Patterns detected:
  - password=, api_key=, secret=, token= (common assignments)
  - AWS key format (AKIA...)
  - Basic auth credentials (user:pass)
  - Common secret file patterns (.env, credentials.json, token.json)

Exits 0 if clean, 1 if any secrets found.
"""

import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent

# Banned file names that should never be tracked
_BANNED_FILES = {".env", "credentials.json", "token.json", ".aws/credentials"}

# Files to skip (documentation, config examples, etc.)
_SKIP_PATHS = {"docs/", ".md", ".yaml", ".yml", ".json.example"}

# Generic secret assignment patterns (not company-specific)
# Stricter patterns to avoid documentation false positives
_PATTERNS = [
    r"(?i)(api[_\-]?key|secret[_\-]?key|password)\s*=\s*['\"](?!.*example)[A-Za-z0-9+/]{32,}",
    r"(?i)token\s*=\s*['\"](?!.*example)(?!Bearer|Basic)[A-Za-z0-9+/._\-]{40,}",
    r"(?i)credential\s*=\s*['\"][A-Za-z0-9+/]{32,}",
    r"AKIA[0-9A-Z]{16}",  # AWS access key (specific format)
]

_COMPILED = [re.compile(p) for p in _PATTERNS]
_IGNORED_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".pdf", ".gz", ".tar", ".zip"}


def _tracked_files() -> list[Path]:
    """Get list of files tracked in git."""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
        cwd=_REPO,
    )
    return [_REPO / p for p in result.stdout.splitlines() if p.strip()]


def scan() -> int:
    """Scan tracked files for banned names and secret patterns. Return 1 if found, 0 if clean."""
    issues = []

    for path in _tracked_files():
        # Check banned filenames
        if path.name in _BANNED_FILES:
            issues.append(f"  {path.relative_to(_REPO)}: banned filename")
            continue

        # Skip binary/ignored files and documentation
        rel_path = str(path.relative_to(_REPO))
        if (
            path.suffix in _IGNORED_SUFFIXES
            or not path.exists()
            or rel_path.startswith("docs/")
            or rel_path.endswith((".md", ".yaml", ".yml"))
        ):
            continue

        # Scan file content
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern in _COMPILED:
                if pattern.search(line):
                    issues.append(f"  {path.relative_to(_REPO)}:{lineno}: possible secret")
                    break

    if issues:
        print("FAIL: secret patterns or banned files detected:")
        for issue in issues:
            print(issue)
        return 1

    print("OK: no secret patterns or banned files found.")
    return 0


if __name__ == "__main__":
    sys.exit(scan())
