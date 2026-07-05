# Security Checks Strategy

This document outlines the three-tier security check infrastructure protecting this
repository from accidental exposure of secrets, credentials, and sensitive data.

## Overview: Three-Tier Defense

| Tier | Tool | Scope | Public/Private | Enforcement |
|------|------|-------|---|---|
| **Tier 1: Committed** | `.pre-commit-config.yaml` + `scripts/check-secrets.py` | Generic secret patterns (passwords, API keys, tokens, credit cards) | Public (in repo) | Pre-commit hook + CI |
| **Tier 2: Local-Only** | `.git/hooks/pre-commit` (local, not committed) | Company/project-specific patterns (domains, customer IDs, team names) | Private (local only) | Pre-commit hook only |
| **Tier 3: Runtime** | Monitoring & alerting (external systems) | Live detection, post-breach response, audit logs | Private (server-side) | Incident response |

---

## Tier 1: Committed Generic Secret Scanning

**What it catches:**
- Assignments like `password=`, `api_key=`, `secret=`, `token=` followed by long strings
- AWS access key patterns (`AKIA...`)
- Bearer token patterns
- Basic auth credentials
- Banned files (`.env`, `credentials.json`, `token.json`)

**Why it's public (in the repo):**
- Patterns are generic and not tied to our specific infrastructure
- Revealing what we scan for doesn't compromise security (patterns are obvious)
- Team accountability: standards are transparent and enforced for everyone
- CI visibility: failures are logged and block merges

**How it runs:**

*Locally (before commit):*
```bash
pre-commit run --all-files  # Or automatically on git commit
```

*In CI (on every PR):*
```bash
uv run python scripts/check-secrets.py
```

**Files involved:**
- `scripts/check-secrets.py` — the scanner (generic patterns)
- `.pre-commit-config.yaml` — local hook registration
- `.github/workflows/ci.yml` — CI enforcement
- `README.md` — documentation of how to run checks locally

---

## Tier 2: Local-Only Company-Specific Patterns

**What goes here:**
- Internal domain names (e.g., `internal.company.com`)
- Customer ID formats specific to your business
- Employee naming patterns (if you use consistent naming)
- Proprietary constant names or secret variable names
- Any pattern that would reveal your infrastructure or operations

**Why it's local-only (NOT committed):**
- Revealing what patterns you check for = revealing what you're protecting
- If an attacker knows what patterns you look for, they can evade checks
- Keeps your operational security opaque
- No version control: easier to update without git history

**How to set it up:**

1. **Copy the template to your local hooks:**
   ```bash
   cp .git/hooks/pre-commit.template .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

2. **Customize with YOUR patterns** (examples in the template):
   ```bash
   # Add checks for patterns specific to your org
   if git diff --cached | grep -q "internal.company.com"; then
     echo "FAIL: internal domain leaked"
     exit 1
   fi
   ```

3. **Run automatically on commit:**
   The hook runs before every commit. To bypass:
   ```bash
   git commit --no-verify  # NOT recommended
   ```

**Alternative: Global hooks (applies to all repos):**
```bash
mkdir -p ~/.git-hooks-private
cp .git/hooks/pre-commit.template ~/.git-hooks-private/pre-commit
chmod +x ~/.git-hooks-private/pre-commit
git config --global core.hooksPath ~/.git-hooks-private
```

**Note:** `.git/hooks/` is local and not version-controlled, so changes don't
appear in `git diff` or git history.

---

## Tier 3: Runtime Monitoring (Server-Side, External)

This tier is not implemented in the repository itself. In production:

- **Monitoring systems** (e.g., log aggregation, secret scanning services)
  detect compromised patterns in real-time
- **Alerting** notifies on-call when a credential is used unexpectedly
- **Audit logs** track who accessed what credentials and when
- **Post-breach response** revokes compromised credentials

Examples:
- Monitor GitHub API audit logs for suspicious token usage
- Alert if a staging database password is used in production logs
- Scan production logs for hardcoded secrets in error messages

---

## What Each Check Does

### 1. `check-secrets.py` (Tier 1: Committed)

**Purpose:** Detect accidental commits of credentials and banned files.

**Patterns detected:**
```regex
password=      → password=mysecret123
api_key=       → api_key="sk_live_1234567890"
secret=        → secret=super_secret_value
token=         → token=eyJhbGciOiJIUzI1NiI...
aws key        → AKIA1234567890ABCDEF
bearer token   → Bearer eyJhbGciOiJIUzI1NiI...
basic auth     → Basic dXNlcjpwYXNz
```

**Banned files:**
- `.env` (environment variables)
- `credentials.json` (OAuth credentials)
- `token.json` (user tokens)
- `.aws/credentials` (AWS config)

**How to run:**
```bash
python3 scripts/check-secrets.py       # Standalone
uv run python scripts/check-secrets.py  # Via uv
pre-commit run --all-files              # Via pre-commit
```

**Exit codes:**
- `0` — clean (no secrets found)
- `1` — failure (secrets detected, prints details)

### 2. Pre-commit Hooks (Both Tiers)

Tier 1 (public) checks run automatically via `.pre-commit-config.yaml`:
- `check-secrets.py` — generic pattern scan
- `ruff check` — code quality
- Line cap checks, link validation, etc.

Tier 2 (local-only) checks run from `.git/hooks/pre-commit`:
- Custom patterns you define (not in repo)
- Company-specific checks

Both are triggered on `git commit`. Both can be bypassed with `--no-verify`
(not recommended for security checks).

### 3. CI Enforcement (Tier 1: Committed)

`.github/workflows/ci.yml` runs `check-secrets.py` on every PR. Failures block merge.

This ensures code cannot land without passing the generic secret scan.

---

## Best Practices

### ✅ DO:
- **Commit generic checks** (ruff, line caps, secret patterns everyone knows about)
- **Keep local hooks private** (never commit `.git/hooks/` with your patterns)
- **Use global hooks** if the same pattern applies to all your repos
- **Document publicly** what generic patterns you scan for (in README, CLAUDE.md)
- **Test your patterns** before committing: `python scripts/check-secrets.py`
- **Bypass only when certain:** `git commit --no-verify` should be rare

### ❌ DON'T:
- **Commit company-specific patterns** to `.git/hooks/pre-commit` (it's local)
- **Hardcode credentials** anywhere, even in tests or documentation
- **Rely on pre-commit alone** — it can be bypassed (--no-verify)
- **Make pre-commit hooks too strict** — false positives block legitimate commits
- **Assume CI is the final gate** — run checks locally first

---

## Troubleshooting

### Pre-commit hook isn't running

1. **Verify installation:**
   ```bash
   uv run pre-commit install
   git config core.hooksPath  # Should be empty or point to .git/hooks
   ```

2. **Run manually to test:**
   ```bash
   uv run pre-commit run --all-files
   ```

3. **Check hook is executable:**
   ```bash
   ls -la .git/hooks/pre-commit  # Should have 'x' permission
   ```

### False positives in check-secrets.py

If you get a false positive (legitimate string matching a secret pattern):
1. Check the file and line number in the error output
2. Verify it's not actually a secret
3. Add the file/pattern to `.pre-commit-config.yaml` exclusions (if needed)
4. Or add a more specific pattern to Tier 2 (local) to suppress it locally

### How do I bypass the check?

```bash
git commit --no-verify  # Skips all pre-commit hooks (not recommended)
```

Only use this if you're absolutely certain the file is safe, and consider why
the check flagged it.

---

## Examples: What Gets Caught

### Will catch:
```python
# Tier 1 catches:
API_KEY = "sk_live_1234567890"
password = "super_secret_123"
SECRET = "aws_secret_access_key_value"
BEARER_TOKEN = "Bearer eyJhbGciOiJIUzI1NiI..."
aws_access_key = "AKIA1234567890ABCDEF"
```

### Will NOT catch (by design):
```python
# Generic patterns, so these pass Tier 1:
x = "mypassword123"  # String literal, not assignment
description = "This password policy requires..."  # Not an assignment
"""Password reset instructions..."""  # Comment, not code secret
# api_key = "secret"  # Commented out

# Tier 2 (local) would catch:
url = "https://internal.company.com/api"
customer_id = "cust_ABC12345"
email = "alice@company.com"
```

---

## References

- `.pre-commit-config.yaml` — local pre-commit hooks registration
- `.git/hooks/pre-commit.template` — template for company-specific local hooks
- `scripts/check-secrets.py` — the generic secret scanner
- `.github/workflows/ci.yml` — CI enforcement
- `README.md` — how to run quality gates locally
- `CLAUDE.md` — project development standards
