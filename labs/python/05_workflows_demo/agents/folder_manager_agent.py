from agent_framework import ChatAgent
from tools.mcp_tools import create_directory, list_directory

def build_folder_manager_agent(chat_client):
    """
    Agent responsible for creating research folders using MCP filesystem tools.
    It ensures the base path exists, checks for name collisions,
    and returns the created folder path.
    """
    return ChatAgent(
        name="FolderManagerAgent",
        description="Creates and manages research folders on disk via MCP filesystem tools.",
        instructions=(
            "Given a research title or topic, sanitize it to a safe folder name "
            "(snake_case, lowercase). Use 'list_directory' to inspect existing folders "
            "under '/mnt/research', and 'create_directory' to make a new one. "
            "If a folder with the same name exists, append a counter suffix (_2, _3, etc.). "
            "Return the full path of the created folder."
        ),
        chat_client=chat_client,
        tools=[list_directory, create_directory],
    )
