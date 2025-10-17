# main.py

from agent_framework.devui import DevServer
from config import DEVUI_HOST, DEVUI_PORT, MCP_GATEWAY_URL
import asyncio
import uvicorn

from agents import AgentFactory
from persistence.checkpoint_storage_factory import CheckpointStorageFactory
from tools import mcp_tools
from tools.mcp_gateway_client import MCPGatewayClient
from workflows.workflow_factory import WorkflowFactory

async def main():
    
    # MCP Gateway initialization
    mcp_client = MCPGatewayClient(MCP_GATEWAY_URL)
    await mcp_client.connect()
    await mcp_client.list_tools()

    # Make it available to all MCP tools
    mcp_tools.init_mcp_client(mcp_client)

    # Init
    factory = AgentFactory().init_defaults()
    storage_factory = CheckpointStorageFactory()
    checkpoint_storage = await storage_factory.init_postgres()

    # Build all workflows
    wf_factory = WorkflowFactory(factory, checkpoint_storage).init_defaults()

    # Register in DevUI
    server = DevServer(host=DEVUI_HOST, port=DEVUI_PORT, ui_enabled=True)
    server.register_entities([*factory.all(), *wf_factory.all()])
    
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
