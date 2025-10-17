# agents/fetch_agent.py
from agent_framework import ChatAgent
from tools.mcp_tools import fetch_webpage

def build_fetch_agent(chat_client):
    return ChatAgent(
        name="FetchAgent",
        description="Fetches webpage content via MCP Fetch tool and summarizes key information.",
        instructions=(
            "Given a list of URLs, use 'fetch_webpage' to retrieve their content. "
            "Summarize the most relevant insights from each page as short paragraphs separated by '---'."
        ),
        chat_client=chat_client,
        tools=[fetch_webpage],
    )
