"""
Lab P03 - Agentic Reasoning 🧩
Sense → Plan → Act → Reflect using Microsoft Agent Framework for Python
with Docker Model Runner (LLM backend) + Hosted MCP tools (DuckDuckGo / Fetch).

Prereqs:
    pip install agent-framework openai colorama python-dotenv
"""

import asyncio, os
from dotenv import load_dotenv
from agent_framework import ChatAgent, HostedMCPTool, MCPStdioTool
from agent_framework.openai import OpenAIChatClient
from echo import Echo

# ───────────────────────────────
# 1. Environment + Client
# ───────────────────────────────
load_dotenv()
Echo.info("Lab P03 - Agentic Reasoning (Sense → Plan → Act → Reflect)")

base_url = os.getenv("OPENAI_API_BASE", "http://localhost:12434/engines/llama.cpp/v1")
api_key  = os.getenv("OPENAI_API_KEY", "none")
model_id = os.getenv("MODEL_ID", "ai/gpt-oss:latest")

Echo.system(f"Endpoint : {base_url}")
Echo.system(f"Model    : {model_id}")

chat_client = OpenAIChatClient(base_url=base_url, api_key=api_key, model_id=model_id)

# ───────────────────────────────
# 3. Agent Definition (SPAR loop)
# ───────────────────────────────
instructions = """
You are a self-sufficient research agent.
When the user asks about a topic:
1. Sense → Identify the intent.
2. Plan  → Decide which tools to call and in what order.
3. Act   → Invoke DuckDuckGo (search) and Fetch (retrieve).
4. Reflect → Verify coverage and summarize findings.
Explain your reasoning briefly before the final answer.
"""



# ───────────────────────────────
# 4. Interactive Run (Stream)
# ───────────────────────────────
async def main():
    Echo.step("🔧 Initializing Hosted MCP tools …")

    duck = MCPStdioTool(
        name="DuckDuckGo",
        command="docker",
        args=["run", "-i", "--rm", "mcp/duckduckgo"],
        chat_client=chat_client,
    )
    fetch = MCPStdioTool(
        name="Fetch",
        command="docker",
        args=["run", "-i", "--rm", "mcp/fetch"],
        chat_client=chat_client,
    )

    try:
        async with duck, fetch:
            all_tools = [*duck.functions, *fetch.functions]

            agent = ChatAgent(
                chat_client=chat_client,
                instructions=instructions,
                name="ResearchAgent",
                tools=all_tools
            )
            Echo.system(f"Tools    : {', '.join(tool.name for tool in all_tools)}")

            thread = agent.get_new_thread()
            Echo.user("Tell me what you want to research:")
            query = input().strip() or (
                "Combine Microsoft Agent Framework with Docker Model Runner. "
                "Generate a Python experiment recipe. I want you do a deep research and provide a detailed implementation plan."
            )

            Echo.user(query)
            Echo.system(f"Running agentic loop for '{query}' …\n")

            await Echo.stream_agent_async(agent.run_stream(query, thread=thread))

        Echo.done("Reasoning cycle complete.")
        Echo.system("Close the window or press Ctrl+C to exit.")
    except Exception as ex:
        Echo.error(f"MCP initialization failed: {ex}")


if __name__ == "__main__":
    asyncio.run(main())
