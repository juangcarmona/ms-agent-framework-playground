# agents/pure_fetch_agent.py
from agent_framework import ChatAgent
from tools.mcp_tools import fetch_webpage

def build_pure_fetch_agent(chat_client):
    return ChatAgent(
        name="PureFetcherAgent",
        description="Fetches webpage content via MCP Fetch tool without summarizing.",
        instructions=(
            "Use 'fetch_webpage' to retrieve the raw textual or markdown content of the given URLs. "
            "Do not summarize or interpret; just return the fetched text as-is."
        ),
        chat_client=chat_client,
        tools=[fetch_webpage],
    )
