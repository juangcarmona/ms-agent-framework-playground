# agents/general_agent.py
from agent_framework import ChatAgent

def build_general_agent(chat_client):
    return ChatAgent(
        name="GeneralAgent",
        description="Answers general questions or explains concepts clearly.",
        instructions="Respond clearly and informatively to any general user question or topic.",
        chat_client=chat_client,
    )
