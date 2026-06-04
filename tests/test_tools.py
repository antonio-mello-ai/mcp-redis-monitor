"""Tests for MCP Redis Monitor tools with mocked Redis connections."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_redis(
    *,
    keys: list[str] | None = None,
    key_types: dict[str, str] | None = None,
    key_lengths: dict[str, int] | None = None,
    info_data: dict[str, object] | None = None,
    list_data: dict[str, list[str]] | None = None,
) -> AsyncMock:
    """Build an AsyncMock that behaves like redis.asyncio.Redis."""
    keys = keys or []
    key_types = key_types or {}
    key_lengths = key_lengths or {}
    info_data = info_data or {}
    list_data = list_data or {}

    mock = AsyncMock()

    # scan returns (0, keys) — single pass
    mock.scan.return_value = (0, keys)

    # type
    async def _type(k: str) -> str:
        return key_types.get(k, "string")

    mock.type = AsyncMock(side_effect=_type)

    # length helpers
    mock.strlen = AsyncMock(side_effect=lambda k: key_lengths.get(k, 0))
    mock.llen = AsyncMock(side_effect=lambda k: key_lengths.get(k, 0))
    mock.scard = AsyncMock(side_effect=lambda k: key_lengths.get(k, 0))
    mock.zcard = AsyncMock(side_effect=lambda k: key_lengths.get(k, 0))
    mock.hlen = AsyncMock(side_effect=lambda k: key_lengths.get(k, 0))
    mock.xlen = AsyncMock(side_effect=lambda k: key_lengths.get(k, 0))

    # lindex for celery
    async def _lindex(k: str, idx: int) -> str | None:
        items = list_data.get(k, [])
        if 0 <= idx < len(items):
            return items[idx]
        return None

    mock.lindex = AsyncMock(side_effect=_lindex)

    # info
    async def _info(section: str = "") -> dict:
        return info_data.get(section, {})  # type: ignore[return-value]

    mock.info = AsyncMock(side_effect=_info)
    mock.aclose = AsyncMock()

    return mock


@asynccontextmanager
async def _patched_redis(mock_redis: AsyncMock):
    """Context manager matching get_redis signature."""
    yield mock_redis


# ---------------------------------------------------------------------------
# Tests — queues
# ---------------------------------------------------------------------------


class TestGetQueueDepths:
    @pytest.mark.asyncio
    async def test_returns_keys_with_lengths(self) -> None:
        mock = _make_mock_redis(
            keys=["mylist", "myhash"],
            key_types={"mylist": "list", "myhash": "hash"},
            key_lengths={"mylist": 5, "myhash": 3},
        )

        with patch(
            "mcp_redis_monitor.tools.queues.get_redis",
            return_value=_patched_redis(mock),
        ):
            from mcp_redis_monitor.tools.queues import get_queue_depths

            result = json.loads(await get_queue_depths(db=3))

        assert result["db"] == 3
        assert result["total_keys"] == 2
        keys_map = {k["key"]: k for k in result["keys"]}
        assert keys_map["mylist"]["type"] == "list"
        assert keys_map["mylist"]["length"] == 5
        assert keys_map["myhash"]["type"] == "hash"
        assert keys_map["myhash"]["length"] == 3

    @pytest.mark.asyncio
    async def test_empty_db(self) -> None:
        mock = _make_mock_redis(keys=[])

        with patch(
            "mcp_redis_monitor.tools.queues.get_redis",
            return_value=_patched_redis(mock),
        ):
            from mcp_redis_monitor.tools.queues import get_queue_depths

            result = json.loads(await get_queue_depths())

        assert result["total_keys"] == 0


class TestGetCeleryQueueStatus:
    @pytest.mark.asyncio
    async def test_finds_celery_queues(self) -> None:
        task_body = json.dumps({"headers": {"id": "abc-123"}})
        mock = _make_mock_redis(
            keys=["celery", "some_string_key"],
            key_types={"celery": "list", "some_string_key": "string"},
            key_lengths={"celery": 2},
            list_data={"celery": [task_body]},
        )

        with patch(
            "mcp_redis_monitor.tools.queues.get_redis",
            return_value=_patched_redis(mock),
        ):
            from mcp_redis_monitor.tools.queues import get_celery_queue_status

            result = json.loads(await get_celery_queue_status())

        assert result["total_queues"] == 1
        assert result["queues"][0]["queue"] == "celery"
        assert result["queues"][0]["pending"] == 2
        assert result["queues"][0]["oldest_task_id"] == "abc-123"


# ---------------------------------------------------------------------------
# Tests — info
# ---------------------------------------------------------------------------


class TestGetConnectedClients:
    @pytest.mark.asyncio
    async def test_returns_client_count(self) -> None:
        mock = _make_mock_redis(info_data={"clients": {"connected_clients": 42}})

        with patch(
            "mcp_redis_monitor.tools.info.get_redis",
            return_value=_patched_redis(mock),
        ):
            from mcp_redis_monitor.tools.info import get_connected_clients

            result = json.loads(await get_connected_clients())

        assert result["connected_clients"] == 42


class TestGetServerInfo:
    @pytest.mark.asyncio
    async def test_returns_memory_uptime_keyspace(self) -> None:
        mock = _make_mock_redis(
            info_data={
                "memory": {
                    "used_memory_human": "1.50M",
                    "used_memory_peak_human": "2.00M",
                    "maxmemory_human": "0B",
                    "mem_fragmentation_ratio": 1.2,
                },
                "server": {
                    "uptime_in_seconds": 86400,
                    "uptime_in_days": 1,
                },
                "keyspace": {
                    "db0": {"keys": 100, "expires": 10, "avg_ttl": 5000},
                },
            }
        )

        with patch(
            "mcp_redis_monitor.tools.info.get_redis",
            return_value=_patched_redis(mock),
        ):
            from mcp_redis_monitor.tools.info import get_server_info

            result = json.loads(await get_server_info())

        assert result["memory"]["used_memory_human"] == "1.50M"
        assert result["uptime"]["uptime_in_days"] == 1
        assert "db0" in result["keyspace"]


class TestGetKeyCountByDb:
    @pytest.mark.asyncio
    async def test_returns_db_key_counts(self) -> None:
        mock = _make_mock_redis(
            info_data={
                "keyspace": {
                    "db0": {"keys": 100, "expires": 5, "avg_ttl": 0},
                    "db3": {"keys": 42, "expires": 0, "avg_ttl": 0},
                },
            }
        )

        with patch(
            "mcp_redis_monitor.tools.info.get_redis",
            return_value=_patched_redis(mock),
        ):
            from mcp_redis_monitor.tools.info import get_key_count_by_db

            result = json.loads(await get_key_count_by_db())

        assert result["databases"]["db0"] == 100
        assert result["databases"]["db3"] == 42
        assert result["total_databases"] == 2
