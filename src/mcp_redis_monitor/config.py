"""Redis connection configuration from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RedisConfig:
    """Read-only Redis connection configuration."""

    host: str
    port: int
    password: str | None

    @classmethod
    def from_env(cls) -> RedisConfig:
        """Build config from REDIS_MONITOR_* environment variables."""
        return cls(
            host=os.getenv("REDIS_MONITOR_HOST", "localhost"),
            port=int(os.getenv("REDIS_MONITOR_PORT", "6379")),
            password=os.getenv("REDIS_MONITOR_PASSWORD") or None,
        )
