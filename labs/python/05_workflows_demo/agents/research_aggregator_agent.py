# agents/research_aggregator_agent.py
from agent_framework import ChatAgent
from tools.filesystem import read_file, list_directory, write_file

def build_research_aggregator_agent(chat_client):
    return ChatAgent(
        name="ResearchAggregatorAgent",
        description="Synthesizes multiple TL;DRs into a global research summary.",
        instructions=(
            "Given several TL;DR sections from related articles, "
            "synthesize them into a comprehensive research summary. "
            "Highlight consensus points, key findings, and overall conclusions."
            "Write the final summary to a file named 'research_summary.md'  with proper markdown formatting."
        ),
        chat_client=chat_client,
        tools=[read_file, write_file, list_directory],
    )
