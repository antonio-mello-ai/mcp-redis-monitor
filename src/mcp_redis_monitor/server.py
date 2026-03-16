"""FastMCP server definition and entry point."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-redis-monitor")

from mcp_redis_monitor.tools import info, queues  # noqa: E402, F401


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
