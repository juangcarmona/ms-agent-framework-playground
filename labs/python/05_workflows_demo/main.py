# main.py

from agent_framework.devui import DevServer
from config import DEVUI_HOST, DEVUI_PORT, MCP_GATEWAY_URL
import asyncio
import uvicorn

from agents import AgentFactory
from tools import mcp_tools
from tools.mcp_gateway_client import MCPGatewayClient

from workflows.wf01_basic_sequence import build_basic_sequence_workflow
from workflows.wf02_sequential_executors import  build_sequential_executors_workflow
from workflows.wf03_search_and_summarize import build_search_and_summarize_workflow


async def main():
    
    # MCP Gateway initialization
    mcp_client = MCPGatewayClient(MCP_GATEWAY_URL)
    await mcp_client.connect()
    await mcp_client.list_tools()

    # Make it available to all MCP tools
    mcp_tools.init_mcp_client(mcp_client)

    # Initialize and register all agents
    factory = AgentFactory().init_defaults()

    # Build workflows
    wf01 = build_basic_sequence_workflow() 
    wf02 = build_sequential_executors_workflow(factory)
    wf03 = build_search_and_summarize_workflow(factory)

    # Register workflows in DevUI
    server = DevServer(host=DEVUI_HOST, port=DEVUI_PORT, ui_enabled=True)
    server.register_entities([*factory.all(), wf01, wf02, wf03])

    # Start DevUI server
    app = server.get_app()

    config = uvicorn.Config(app=app, host=DEVUI_HOST, port=DEVUI_PORT, loop="asyncio", log_level="info")
    await uvicorn.Server(config).serve()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
    except RuntimeError:
        asyncio.run(main())
