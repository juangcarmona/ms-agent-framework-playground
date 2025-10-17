# agents/markdown_summarizer_agent.py
from agent_framework import ChatAgent

def build_markdown_summarizer_agent(chat_client):
    return ChatAgent(
        name="MarkdownSummarizerAgent",
        description="Creates a detailed TL;DR and structured Markdown summary for an article.",
        instructions=(
            "Given the raw text of an article, produce structured Markdown with:\n"
            "- The original URL in the first line.\n"
            "- A '# TL;DR' section giving a deep, factual summary for later reuse.\n"
            "- Followed by the cleaned or reformatted content as markdown.\n"
            "Avoid hallucination; retain facts."
        ),
        chat_client=chat_client,
    )
