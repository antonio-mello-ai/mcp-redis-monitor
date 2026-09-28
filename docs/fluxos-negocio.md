---
title: Product flows — MCP Redis Monitor
kind: guide
area: product
project: mcp-redis-monitor
collection: mcp-redis-monitor
owner: maintainers
status: current
canonical: docs/fluxos-negocio.md
globalRef: qmd://mcp-redis-monitor/docs/fluxos-negocio.md
reviewCadenceDays: 90
lastReviewedAt: 2026-09-28
sourceRefs:
  - README.md
  - src/mcp_redis_monitor/tools/info.py
  - src/mcp_redis_monitor/tools/queues.py
related:
  - docs/arquitetura.md
  - docs/operacao.md
  - docs/index.md
supersedes: []
supersededBy: []
sensitivity: public
---
# Product flows

MCP Redis Monitor exposes read-only Redis diagnostics to an MCP client. The
operator supplies connection configuration and the client invokes a registered
tool through the stdio server.

## Server overview

- `get_connected_clients` reads the client section of Redis `INFO` and returns
  the connected-client count.
- `get_server_info` combines memory, server uptime and keyspace sections from
  `INFO`.
- `get_key_count_by_db` returns the key count reported for each database in the
  Redis keyspace overview.

Cache efficiency, eviction and fragmentation expansion is tracked in
[Issue #1](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues/1).
Replication and persistence status are tracked in
[Issue #3](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues/3).

## Queue-depth inspection

`get_queue_depths` scans a selected Redis database, reads each key type and
returns a type-appropriate length for strings, lists, sets, sorted sets, hashes
and streams. The current default database is 3.

The current scan is not bounded at the response level. Pagination, work limits
and a safe key-name output policy are tracked in
[Issue #8](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues/8).

## Celery queue inspection

`get_celery_queue_status` scans database 0, considers Redis lists as candidate
queues, reports their pending length and attempts to extract a task ID from the
first list entry. It never removes a message.

The documented Celery detection rule and oldest-message ordering need to be
made explicit and consistent with the implementation; this is tracked in
[Issue #7](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues/7).

## Current boundaries

- The server uses stdio transport.
- Configuration supports host, port and an optional password.
- Each tool call creates and closes its own asynchronous Redis client.
- Tool responses are JSON encoded as text; structured MCP results are tracked
  in [Issue #12](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues/12).
- The repository does not proxy or persist Redis data.
