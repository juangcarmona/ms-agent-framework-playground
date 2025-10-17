# tools/mcp_tools.py
from typing import Annotated, Optional
from .mcp_gateway_client import MCPGatewayClient
import logging

logger = logging.getLogger("mcp_tools")

mcp_client: Optional[MCPGatewayClient] = None


def init_mcp_client(client: MCPGatewayClient):
    """Bind an initialized MCP client for all tools."""
    global mcp_client
    mcp_client = client
    logger.info("MCP client bound to mcp_tools module")


async def search_duckduckgo(
    query: Annotated[str, "DuckDuckGo search query"],
    max_results: Annotated[int, "Max number of results"] = 5,
) -> str:
    if not mcp_client or not mcp_client.session:
        raise RuntimeError("MCP client not initialized")
    return await mcp_client.call_tool("search", {"query": query, "max_results": max_results})


async def fetch_webpage(
    url: Annotated[str, "URL to fetch and parse"]
) -> str:
    if not mcp_client or not mcp_client.session:
        raise RuntimeError("MCP client not initialized")
    try:
        return await mcp_client.call_tool("fetch_content", {"url": url})
    except Exception:
        return await mcp_client.call_tool("fetch", {"url": url})
