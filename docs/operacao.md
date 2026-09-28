---
title: Operations — MCP Redis Monitor
kind: runbook
area: operations
project: mcp-redis-monitor
collection: mcp-redis-monitor
owner: maintainers
status: current
canonical: docs/operacao.md
globalRef: qmd://mcp-redis-monitor/docs/operacao.md
reviewCadenceDays: 90
lastReviewedAt: 2026-09-28
sourceRefs:
  - README.md
  - .env.example
  - .github/workflows/ci.yml
  - .github/workflows/publish.yml
related:
  - docs/fluxos-negocio.md
  - docs/arquitetura.md
  - docs/index.md
supersedes: []
supersededBy: []
sensitivity: public
---
# Operations

## Local installation

```bash
git config core.hooksPath .githooks
uv sync --all-extras --all-groups
```

Configure `REDIS_MONITOR_HOST`, `REDIS_MONITOR_PORT` and, when required,
`REDIS_MONITOR_PASSWORD` outside the repository. `.env.example` contains only
local placeholders.

## Credential and access handling

- Prefer a dedicated Redis ACL identity restricted to the read commands and key
  patterns this monitor requires.
- Do not pass passwords in command-line arguments retained in shell history or
  process listings.
- Do not print credentials, real endpoints, key inventories or queue payloads
  into public issues, terminal transcripts or shared logs.
- Rotate credentials if they are exposed.

The current client does not yet accept an ACL username or TLS configuration;
these production-hardening requirements are tracked in
[Issue #4](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues/4).

## Run

```bash
uv run mcp-redis-monitor
```

The process communicates over stdio. Keep stdout reserved for the MCP protocol;
operational diagnostics must not include credentials or observed payloads.

## Validation

```bash
uv run --all-extras --all-groups pytest -q
uvx ruff check src/ tests/
uvx ruff format --check src/ tests/
gitleaks git --redact --no-banner --log-opts='--all' .
```

CI runs lint, formatting and tests on Python 3.12 and 3.13 for pushes and pull
requests targeting `main`.

## Release

Publishing a GitHub Release triggers the PyPI workflow with trusted publishing.
Before publishing, verify that the Git tag and `pyproject.toml` version agree.
The broken `VERSION`-file expectation in the local pre-push hook is tracked in
[Issue #10](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues/10).

## Failure modes

| Symptom | Check |
| --- | --- |
| Connection refused | Confirm host, port, network reachability and Redis availability. |
| Authentication error | Confirm the injected password and server access policy without printing the secret. |
| Tool call stalls | Timeouts are not yet configurable; see Issue #9. |
| Queue scan is slow or very large | Current scan has no response bound; see Issue #8. |
| Unrelated list appears as a Celery queue | Queue detection is being corrected in Issue #7. |

Roadmap and operational follow-ups belong in GitHub Issues, not in this runbook.
