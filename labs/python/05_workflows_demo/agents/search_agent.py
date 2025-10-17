# agents/search_agent.py
from agent_framework import ChatAgent
from tools.mcp_tools import search_duckduckgo

def build_search_agent(chat_client):
    return ChatAgent(
        name="SearchAgent",
        description="Performs web searches via DuckDuckGo MCP tool.",
        instructions=(
            "Given a topic or question, perform one or more searches using the 'search_duckduckgo' tool. "
            "Return a small list (1–5) of the most relevant URLs as plain text, one per line."
        ),
        chat_client=chat_client,
        tools=[search_duckduckgo],
    )
