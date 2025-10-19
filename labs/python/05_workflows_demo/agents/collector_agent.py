from agent_framework import ChatAgent
from tools.mcp_tools import fetch_webpage
from tools.filesystem import write_file

def build_collector_agent(chat_client):
    """
    Agent that, given a folder and a list of URLs, fetches each page,
    produces markdown summaries (with TL;DR) and writes them as .md files.
    """
    return ChatAgent(
        name="CollectorAgent",
        description="Fetches, summarizes, and saves research articles as Markdown files.",
        instructions=(
            "You are responsible for collecting research sources:\n"
            "- For each given URL, use 'fetch_webpage' to get the full page content.\n"
            "- Create a clean Markdown version starting with the URL on the first line.\n"
            "- Add a '# TL;DR' section with a deep, factual summary.\n"
            "- Write the result to a .md file inside the provided folder using 'write_file'.\n"
            "Ensure filenames are unique and derived from the page title or slug.\n"
            "Return a list of processed filenames or URLs once done."
        ),
        chat_client=chat_client,
        tools=[fetch_webpage, write_file],
    )
