# mcp_gateway_client.py
import logging
from typing import Optional, Dict, Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


class MCPGatewayClient:
    """High-level client for interacting with a Docker MCP Gateway."""

    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
        self.session: Optional[ClientSession] = None
        self._stream_ctx = None
        self._session_ctx = None
        self.logger = logging.getLogger("MCPGatewayClient")

    async def connect(self) -> None:
        """Establish and initialize MCP streaming session."""
        self.logger.info(f"Connecting to MCP Gateway at {self.gateway_url}")
        self._stream_ctx = streamablehttp_client(url=self.gateway_url)
        read_stream, write_stream, _ = await self._stream_ctx.__aenter__()

        self._session_ctx = ClientSession(read_stream, write_stream)
        self.session = await self._session_ctx.__aenter__()

        await self.session.initialize()
        self.logger.info("✅ MCP session initialized")

    async def list_tools(self) -> list[str]:
        """List available tools."""
        assert self.session is not None, "Session not initialized"
        result = await self.session.list_tools()
        tool_names = [t.name for t in result.tools]
        self.logger.info(f"Available tools: {tool_names}")
        return tool_names

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Call a specific tool by name."""
        assert self.session is not None, "Session not initialized"
        self.logger.info(f"Calling MCP tool: {name} with args: {arguments}")
        result = await self.session.call_tool(name=name, arguments=arguments)

        # result.content is a list of content blocks
        if result.content and hasattr(result.content[0], "text"):
            return result.content[0].text
        return str(result)

    async def close(self) -> None:
        """Cleanly close streams."""
        if self._session_ctx:
            await self._session_ctx.__aexit__(None, None, None)
        if self._stream_ctx:
            await self._stream_ctx.__aexit__(None, None, None)
        self.logger.info("🧹 MCP session closed")
