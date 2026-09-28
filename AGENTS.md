---
title: AGENTS.md — MCP Redis Monitor
kind: policy
area: engineering
project: mcp-redis-monitor
collection: mcp-redis-monitor
owner: maintainers
status: current
canonical: AGENTS.md
globalRef: qmd://mcp-redis-monitor/AGENTS.md
reviewCadenceDays: 90
lastReviewedAt: 2026-09-28
sourceRefs:
  - github:antonio-mello-ai/mcp-redis-monitor
related:
  - README.md
  - docs/fluxos-negocio.md
  - docs/arquitetura.md
  - docs/operacao.md
  - docs/index.md
supersedes:
  - CLAUDE.md
  - GEMINI.md
supersededBy: []
sensitivity: public
---
# AGENTS.md — MCP Redis Monitor

## Purpose

This repository provides a public, self-hostable MCP server for read-only Redis
monitoring. Keep code, examples, issues and documentation generic and safe for
public collaboration.

## Public repository boundary

- Never commit Redis passwords, real endpoints, private hostnames, key
  inventories, payloads, local user paths or internal topology.
- Use placeholders and reserved examples in documentation and tests.
- Do not copy operational context from private deployments into this repository.
- Preserve the read-only contract: monitoring tools must not mutate keys,
  queues, configuration or server state.

## Stack

- Python 3.12+
- FastMCP
- redis-py asyncio client
- `uv`, Ruff and pytest

## Local setup and validation

```bash
git config core.hooksPath .githooks
uv sync --all-extras --all-groups
uv run --all-extras --all-groups pytest -q
uvx ruff check src/ tests/
uvx ruff format --check src/ tests/
```

The current versioning inconsistency is tracked in GitHub Issue #10. Do not add
another version source while resolving it.

## Documentation sources of truth

- `README.md`: public installation and usage entry point
- `docs/fluxos-negocio.md`: behavior exposed to MCP clients
- `docs/arquitetura.md`: implementation model and boundaries
- `docs/operacao.md`: self-hosting, credentials, validation and release operation
- `docs/index.md`: navigable documentation index

Roadmap, backlog and priority live in GitHub Issues and the Felhen GitHub
Project. Delivery history lives in closed Issues, pull requests and GitHub
Releases. Do not add `roadmap.md`, `docs/backlog.md` or `CHANGELOG.md`.
