"""Redis async client helper. Creates a connection per call with the specified DB."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis

from mcp_redis_monitor.config import RedisConfig


@asynccontextmanager
async def get_redis(db: int = 0) -> AsyncGenerator[aioredis.Redis, None]:
    """Yield an async Redis client for the given DB, closing it after use."""
    cfg = RedisConfig.from_env()
    client = aioredis.Redis(
        host=cfg.host,
        port=cfg.port,
        password=cfg.password,
        db=db,
        decode_responses=True,
    )
    try:
        yield client
    finally:
        await client.aclose()
