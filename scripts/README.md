# scripts/

Quality-gate scripts wired into pre-commit and CI. Everything runs through
`uv run` so it executes inside the project's resolved environment. None of
these require a submodule or network access.

| Script | Origin | Purpose |
|--------|--------|---------|
| `check_line_cap.py` | pipeline | Line cap: `src`+`tests` raw ≤150; `scripts` logical ≤150 |
| `validate_repo.py` | ex04, rewritten | Project invariants: no personal paths, layer direction (`shared ← providers ← services ← sdk`), config JSON valid; warns on placeholder hardware |
| `check_no_secrets.py` | pipeline | Secret scan over tracked files; bans `.env`, `credentials.json`, `token.json` |
| `check_docs_present.py` | pipeline, list adapted | Required docs/config exist |
| `check_markdown_links.py` | pipeline | Local links in tracked `.md` resolve |
| `check_source_archives.py` | pipeline | No tracked archives (allowlists `.agents/ai-orchestration-skills.zip` — consider untracking it) |
| `check_planning_ids.py` | pipeline | No duplicate `N.M` task-ID rows in `docs/TODO.md` |
| `check_workflow_permissions.py` | pipeline | Every workflow declares minimal `permissions` (needs `pyyaml`) |

## Run the whole suite (exactly as CI does)

```sh
uv run ruff check src tests scripts
uv run python scripts/check_line_cap.py src tests --limit 150 --mode raw
uv run python scripts/check_line_cap.py scripts --limit 150 --mode logical
uv run python scripts/validate_repo.py
uv run python scripts/check_no_secrets.py
uv run python scripts/check_docs_present.py
uv run python scripts/check_markdown_links.py
uv run python scripts/check_source_archives.py
uv run python scripts/check_planning_ids.py
uv run python scripts/check_workflow_permissions.py
uv run pytest --cov=airllm_benchmark --cov-fail-under=85
```

## Notes

- The `## Repository facts` section in `README.md` (test count, module line
  counts, hardware) is maintained by hand — update it when those change.
- A few tests (`tests/pocs/*`, `test_transformers_device.py::TestCpuPath`)
  load real tiny models from HuggingFace and need network; they are the only
  non-keyless tests and are skipped/failed only when offline.

## Deliberately not ported

The game/MCP launchers (`selfplay.py`, `train_qtable.py`, `run_stack.py`,
`run_peer_match.py`, `peer_sync.py`, `launch_common.py`,
`mcp_client_loader.py`), the OpenRouter shim (`openrouter_adapter.py`,
irrelevant to a local-inference benchmark), the LaTeX build chain, and the
`gh`-authenticated milestone tooling all belong to other projects and have no
role here.
