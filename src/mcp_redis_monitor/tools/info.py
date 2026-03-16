"""Server info and client monitoring tools."""

from __future__ import annotations

import json

from mcp_redis_monitor.client import get_redis
from mcp_redis_monitor.server import mcp


@mcp.tool()
async def get_connected_clients() -> str:
    """Get the number of currently connected Redis clients.

    Returns:
        JSON with connected_clients count.
    """
    async with get_redis(db=0) as r:
        info = await r.info("clients")
        return json.dumps(
            {"connected_clients": info.get("connected_clients", 0)},
            indent=2,
        )


@mcp.tool()
async def get_server_info() -> str:
    """Get Redis server info: memory usage, uptime, and keyspace stats.

    Returns:
        JSON with memory, uptime, and keyspace data.
    """
    async with get_redis(db=0) as r:
        memory = await r.info("memory")
        server = await r.info("server")
        keyspace = await r.info("keyspace")

    return json.dumps(
        {
            "memory": {
                "used_memory_human": memory.get("used_memory_human", "N/A"),
                "used_memory_peak_human": memory.get("used_memory_peak_human", "N/A"),
                "maxmemory_human": memory.get("maxmemory_human", "0B"),
                "mem_fragmentation_ratio": memory.get("mem_fragmentation_ratio", 0),
            },
            "uptime": {
                "uptime_in_seconds": server.get("uptime_in_seconds", 0),
                "uptime_in_days": server.get("uptime_in_days", 0),
            },
            "keyspace": {
                db: stats for db, stats in keyspace.items() if db.startswith("db")
            },
        },
        indent=2,
    )


@mcp.tool()
async def get_key_count_by_db() -> str:
    """Get the number of keys in each Redis database (overview).

    Returns:
        JSON mapping database names to their key count.
    """
    async with get_redis(db=0) as r:
        keyspace = await r.info("keyspace")

    databases: dict[str, int] = {}
    for db_name, stats in keyspace.items():
        if db_name.startswith("db"):
            if isinstance(stats, dict):
                databases[db_name] = stats.get("keys", 0)
            else:
                databases[db_name] = 0

    return json.dumps(
        {"databases": databases, "total_databases": len(databases)},
        indent=2,
    )
