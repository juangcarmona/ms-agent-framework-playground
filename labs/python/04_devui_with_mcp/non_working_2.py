import asyncio, os, uvicorn
from dotenv import load_dotenv
from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework.openai import OpenAIChatClient
from agent_framework_devui import DevServer

load_dotenv()

async def main():
    chat_client = OpenAIChatClient(
        base_url=os.getenv("OPENAI_API_BASE", "http://localhost:12434/engines/llama.cpp/v1"),
        api_key=os.getenv("OPENAI_API_KEY", "none"),
        model_id=os.getenv("MODEL_ID", "ai/gpt-oss:latest"),
    )

    async with MCPStreamableHTTPTool(
        name="Local Gateway",
        url="http://localhost:8811/mcp",
        chat_client=chat_client,
    ) as mcp:
        agent = ChatAgent(
            chat_client=chat_client,
            name="ResearchAgent",
            instructions="Sense → Plan → Act → Reflect using available MCP tools.",
            tools=list(mcp.functions),
        )

        server = DevServer(host="0.0.0.0", port=8000, ui_enabled=True)
        server.register_entities([agent])
        app = server.get_app()

        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info", loop="asyncio")
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
