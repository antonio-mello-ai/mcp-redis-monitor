# mcp-redis-monitor

FastMCP server providing read-only tools to monitor Redis instances.

The server reads Redis metadata and queue state over stdio. It does not write,
delete or dequeue data. For production use, configure a dedicated
least-privilege Redis identity; username and TLS support are tracked in
[Issue #4](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues/4).

## Install

```bash
# Run directly with uvx (no install needed)
uvx mcp-redis-monitor

# Or install with pip
pip install mcp-redis-monitor
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_MONITOR_HOST` | `localhost` | Redis host |
| `REDIS_MONITOR_PORT` | `6379` | Redis port |
| `REDIS_MONITOR_PASSWORD` | *(none)* | Redis password (optional) |

## Tools

| Tool | Description |
|------|-------------|
| `get_queue_depths` | Keys + length by type in a specific DB (default: 3) |
| `get_celery_queue_status` | Celery queue names, pending count, oldest task |
| `get_connected_clients` | Number of connected clients |
| `get_server_info` | Memory, uptime, keyspace stats |
| `get_key_count_by_db` | Keys per database (overview) |

## Usage

```bash
mcp-redis-monitor
```

Or add to your MCP client configuration:

```json
{
  "mcpServers": {
    "redis-monitor": {
      "command": "mcp-redis-monitor"
    }
  }
}
```

## Development

```bash
ruff check src/ tests/
ruff format src/ tests/
pytest
```

## License

MIT

## Documentation and roadmap

- [Current product flows](docs/fluxos-negocio.md)
- [Architecture](docs/arquitetura.md)
- [Operations](docs/operacao.md)
- [Documentation index](docs/index.md)
- [Open roadmap items](https://github.com/antonio-mello-ai/mcp-redis-monitor/issues)

Priorities live in GitHub Issues and Projects. Delivery history lives in closed
Issues, pull requests and GitHub Releases.
