---
title: Architecture — MCP Redis Monitor
kind: architecture
area: engineering
project: mcp-redis-monitor
collection: mcp-redis-monitor
owner: maintainers
status: current
canonical: docs/arquitetura.md
globalRef: qmd://mcp-redis-monitor/docs/arquitetura.md
reviewCadenceDays: 90
lastReviewedAt: 2026-09-28
sourceRefs:
  - pyproject.toml
  - src/mcp_redis_monitor
related:
  - docs/fluxos-negocio.md
  - docs/operacao.md
  - docs/index.md
supersedes: []
supersededBy: []
sensitivity: public
---
# Architecture

## Components

| Component | Responsibility |
| --- | --- |
| `server.py` | Creates the FastMCP server, imports tool modules and starts stdio transport. |
| `config.py` | Reads Redis host, port and optional password from environment variables. |
| `client.py` | Creates one asynchronous Redis client for a requested database and closes it after use. |
| `tools/info.py` | Implements client, memory, uptime and keyspace overview tools. |
| `tools/queues.py` | Implements general key-length and Celery list inspection tools. |

## Request path

```text
MCP client
  -> FastMCP tool registration
  -> environment-backed RedisConfig
  -> redis-py asynchronous client
  -> Redis read commands
  -> JSON-encoded text response
```

The server has no application database. The monitored Redis instance remains
the system of record, and the process does not persist observed values.

## Connection boundary

Connection configuration enters through environment variables. The current
client supports host, port, database and optional password. TLS and ACL username
support are tracked in
[Issue #4](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues/4).
Connection and read timeouts are tracked in
[Issue #9](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues/9).

## Read-only boundary

Current tools use Redis metadata and length/read operations such as `INFO`,
`SCAN`, `TYPE`, collection-length commands and `LINDEX`. They do not delete,
acknowledge, dequeue or mutate keys. Explicit MCP read-only/non-destructive
annotations are tracked in
[Issue #11](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues/11).

## Known structural gaps

- Queue scans need bounded pagination and output controls; see Issue #8.
- Celery queue identification and ordering need a precise contract; see Issue #7.
- Responses are JSON strings instead of typed MCP content; see Issue #12.
- Package versioning and the release hook disagree; see Issue #10.
