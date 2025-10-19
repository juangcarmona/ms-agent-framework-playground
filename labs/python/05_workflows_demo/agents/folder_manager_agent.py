from agent_framework import ChatAgent
from tools.filesystem import all_tools


def build_folder_manager_agent(chat_client):
    """
    Agent responsible for creating research folders using local filesystem tools.
    It ensures the base path exists, checks for name collisions,
    and returns the created folder path.
    """
    return ChatAgent(
        name="FolderManagerAgent",
        description="Creates and manages research folders on disk using filesystem tools.",
        instructions=(
            "You manage local research folders inside the current working directory.\n\n"
            "Steps:\n"
            "1. Determine the current working directory using 'get_cwd'.\n"
            "2. Ensure an 'mnt' folder exists within it — create it if missing.\n"
            "3. Inside 'mnt', ensure a 'labp05' folder exists — create it if missing.\n"
            "4. Given a research title or topic, sanitize it to a lowercase, snake_case folder name.\n"
            "5. Check whether that folder already exists inside 'mnt/labp05' using 'list_directory'.\n"
            "6. If a folder with that name exists, append a numeric suffix (_2, _3, etc.) until unique.\n"
            "7. Use 'create_directory' to create the new research folder.\n"
            "8. Return the full absolute path of the created folder, or an error message if something failed.\n\n"
            "Use only the provided tools: 'list_directory' and 'create_directory'."
        ),
        chat_client=chat_client,
        tools=[*all_tools],
    )
