import asyncio
import logging
import os
import uvicorn
from typing import Annotated
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from agent_framework_devui import DevServer
from mcp_gateway_client import MCPGatewayClient

MCP_GATEWAY_URL = os.getenv("MCP_GATEWAY_URL", "http://localhost:8811/mcp")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:12434/engines/llama.cpp/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "none")
MODEL_ID = os.getenv("MODEL_ID", "ai/gpt-oss:latest")

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("mcp-devui")

mcp_client = MCPGatewayClient(MCP_GATEWAY_URL)

# ----------------------------
# Tool wrappers 
# These are plain async funcs that the ChatAgent can call.
# ----------------------------

async def search_duckduckgo(
    query: Annotated[str, "DuckDuckGo search query"],
    max_results: Annotated[int, "Max number of results"] = 5,
) -> str:
    """
    Uses the DuckDuckGo MCP server's 'search' tool.
    Make sure your gateway enables the duckduckgo server.
    """
    return await mcp_client.call_tool("search", {"query": query, "max_results": max_results})


async def fetch_webpage(
    url: Annotated[str, "URL to fetch and parse"],
) -> str:
    """
    Uses the Fetch MCP server's 'fetch_content' (or similar) tool name.
    """
    # Common names across my examples: "fetch_content", "fetch"
    try:
        return await mcp_client.call_tool("fetch_content", {"url": url})
    except Exception:
        # fallback if your MCP server registers as "fetch"
        return await mcp_client.call_tool("fetch", {"url": url})
    
agent = ChatAgent(
    name="LocalMCPAgent",
    description="Agent that uses locally hosted MCP tools via Docker MCP Gateway.",
    instructions=(
        "You are a research assistant. When asked about topics on the web, "
        "use 'search_duckduckgo' to find sources, then 'fetch_webpage' to read and summarize them. "
    ),
    chat_client=OpenAIChatClient(
        base_url=OPENAI_API_BASE,
        api_key=OPENAI_API_KEY,
        model_id=MODEL_ID,
    ),
    tools=[
        search_duckduckgo,
        fetch_webpage
    ],
)


# ----------------------------
# DevUI (Uvicorn) —> async-safe runner
# ----------------------------
async def main():
    # 1) Connect MCP once and print available tools
    await mcp_client.connect()
    await mcp_client.list_tools()

    # 2) DevUI app
    server = DevServer(host="0.0.0.0", port=8000, ui_enabled=True)
    server.register_entities([agent])
    app = server.get_app()

    # 3) Run Uvicorn in this event loop
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info", loop="asyncio")
    await uvicorn.Server(config).serve()

    # 4) Cleanup
    await mcp_client.close()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
    except RuntimeError:
        asyncio.run(main())