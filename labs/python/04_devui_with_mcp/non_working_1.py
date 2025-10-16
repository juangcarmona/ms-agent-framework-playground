# labs/python/04_devui_feelings/main.py

from agent_framework import ChatAgent, MCPStdioTool
from agent_framework_devui import DevServer
from agent_framework.openai import OpenAIChatClient
from agent_framework_devui import DevServer
from devui_patch import DevUIPatch
from dotenv import load_dotenv
from echo import Echo
import asyncio, os
import logging
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def main():
    Echo.info("Lab 04 - DevUI Same Loop")

    base_url = os.getenv("OPENAI_API_BASE", "http://localhost:12434/engines/llama.cpp/v1")
    api_key  = os.getenv("OPENAI_API_KEY", "none")
    model_id = os.getenv("MODEL_ID", "ai/gpt-oss:latest")
    chat_client = OpenAIChatClient(base_url=base_url, api_key=api_key, model_id=model_id)

    duck = MCPStdioTool(name="DuckDuckGo", command="docker", args=["run", "-i", "--rm", "mcp/duckduckgo"], chat_client=chat_client)
    fetch = MCPStdioTool(name="Fetch",      command="docker", args=["run", "-i", "--rm", "mcp/fetch"],      chat_client=chat_client)

    async with duck, fetch:
        tools = [*duck.functions, *fetch.functions]

        agent = ChatAgent(
            chat_client=chat_client,
            name="ResearchAgent",
            instructions=(
                "You are a self-sufficient research agent. "
                "Sense → Plan → Act → Reflect using DuckDuckGo and Fetch."
            ),
            tools=tools,
        )

        server = DevServer(host="0.0.0.0", port=8000, ui_enabled=True)
        server.register_entities([agent])
        DevUIPatch.apply(server)   # cleanly patch instance
        app = server.get_app()

        Echo.system(f"Tools registered: {', '.join(t.name for t in tools)}")
        Echo.step("Launching DevUI (same loop)… http://0.0.0.0:8000")

        # Run uvicorn within THIS event loop; blocks until shutdown
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info", loop="asyncio")
        uv_server = uvicorn.Server(config)
        await uv_server.serve()

if __name__ == "__main__":
    asyncio.run(main())
