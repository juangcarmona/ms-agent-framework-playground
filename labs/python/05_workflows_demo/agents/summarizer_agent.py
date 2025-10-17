# agents/summarizer_agent.py
from agent_framework import ChatAgent

def build_summarizer_agent(chat_client):
    return ChatAgent(
        name="SummarizerAgent",
        description="Summarizes a conversation or text passage concisely.",
        instructions="Summarize the key points from the provided conversation or text, keeping meaning intact but concise.",
        chat_client=chat_client,
    )
