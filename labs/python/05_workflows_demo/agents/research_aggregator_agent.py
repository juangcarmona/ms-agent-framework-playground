# agents/research_aggregator_agent.py
from agent_framework import ChatAgent

def build_research_aggregator_agent(chat_client):
    return ChatAgent(
        name="ResearchAggregatorAgent",
        description="Synthesizes multiple TL;DRs into a global research summary.",
        instructions=(
            "Given several TL;DR sections from related articles, "
            "synthesize them into a comprehensive research summary. "
            "Highlight consensus points, key findings, and overall conclusions."
        ),
        chat_client=chat_client,
    )
