# agents/title_generator_agent.py
from agent_framework import ChatAgent

def build_title_generator_agent(chat_client):
    return ChatAgent(
        name="TitleGeneratorAgent",
        description="Generates short, descriptive titles summarizing input topics.",
        instructions="Create a concise, human-readable title summarizing the given text or conversation.",
        chat_client=chat_client,
    )
