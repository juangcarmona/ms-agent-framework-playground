# agents/search_agent.py
from agent_framework import ChatAgent
from tools.mcp_tools import search_duckduckgo

def build_search_agent(chat_client):
    return ChatAgent(
        name="SearchAgent",
        description="Performs the initial research step: searches the web and extracts the most relevant URLs.",
        instructions=(
            "You are a research assistant specializing in web discovery. "
            "Given a topic, question, or request for information, perform a DuckDuckGo search "
            "using the available 'search_duckduckgo' tool. "
            "Analyze the results and extract the 5-10 most relevant URLs that directly address the topic. "
            "Return ONLY a JSON array of URLs — one per element, without commentary, markdown, or explanations. "
            "Each URL must start with 'http' or 'https'. "
            "If the search results contain noise, filter to include only authoritative or meaningful sources."
        ),
        chat_client=chat_client,
        tools=[search_duckduckgo],
    )
