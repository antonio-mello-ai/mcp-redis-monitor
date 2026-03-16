"""Queue monitoring tools."""

from __future__ import annotations

import json

from mcp_redis_monitor.client import get_redis
from mcp_redis_monitor.server import mcp


@mcp.tool()
async def get_queue_depths(db: int = 3) -> str:
    """Get keys and their length by type in a specific Redis DB.

    Args:
        db: Redis database number (default: 3).

    Returns:
        JSON with key names, types, and sizes.
    """
    results: list[dict[str, str | int]] = []
    async with get_redis(db=db) as r:
        cursor = 0
        while True:
            cursor, keys = await r.scan(cursor=cursor, count=100)
            for key in keys:
                key_type = await r.type(key)
                length = await _get_key_length(r, key, key_type)
                results.append({"key": key, "type": key_type, "length": length})
            if cursor == 0:
                break
    return json.dumps({"db": db, "keys": results, "total_keys": len(results)}, indent=2)


async def _get_key_length(r, key: str, key_type: str) -> int:  # type: ignore[type-arg]
    """Return the length/size of a key based on its type."""
    match key_type:
        case "string":
            return await r.strlen(key)
        case "list":
            return await r.llen(key)
        case "set":
            return await r.scard(key)
        case "zset":
            return await r.zcard(key)
        case "hash":
            return await r.hlen(key)
        case "stream":
            return await r.xlen(key)
        case _:
            return 0


@mcp.tool()
async def get_celery_queue_status() -> str:
    """Get Celery queue names, pending task count, and oldest task age.

    Scans DB 0 for Celery list-based queues (convention: keys without
    ':' prefix that are lists).

    Returns:
        JSON with queue names, pending counts, and oldest task info.
    """
    queues: list[dict[str, object]] = []
    async with get_redis(db=0) as r:
        cursor = 0
        while True:
            cursor, keys = await r.scan(cursor=cursor, count=100)
            for key in keys:
                key_type = await r.type(key)
                if key_type != "list":
                    continue
                pending = await r.llen(key)
                oldest_task: str | None = None
                if pending > 0:
                    raw = await r.lindex(key, 0)
                    if raw:
                        try:
                            body = json.loads(raw)
                            oldest_task = body.get("headers", {}).get("id")
                        except (json.JSONDecodeError, AttributeError):
                            oldest_task = "(unparseable)"
                queues.append(
                    {
                        "queue": key,
                        "pending": pending,
                        "oldest_task_id": oldest_task,
                    }
                )
            if cursor == 0:
                break
    return json.dumps({"queues": queues, "total_queues": len(queues)}, indent=2)
