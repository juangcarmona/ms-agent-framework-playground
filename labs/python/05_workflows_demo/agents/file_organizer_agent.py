# agents/file_organizer_agent.py
from agent_framework import ChatAgent
from tools.filesystem import (
    list_directory,
    search_files,
    move_file,
    read_file,
    write_file,
    create_directory,
)

def build_file_organizer_agent(chat_client):
    """
    Agent that organizes and manages local folders and documents.
    """
    return ChatAgent(
        name="FileOrganizerAgent",
        description="Manages and organizes files, performs searches, and edits text documents.",
        instructions=(
            "You are a local file manager assistant.\n"
            "- Use 'list_directory' to see contents.\n"
            "- Use 'search_files' to find documents.\n"
            "- Use 'read_file' or 'write_file' to inspect or update content.\n"
            "- Use 'move_file' and 'create_directory' to organize files.\n"
            "Always confirm the operations you performed and summarize results clearly."
        ),
        chat_client=chat_client,
        tools=[
            list_directory,
            search_files,
            move_file,
            read_file,
            write_file,
            create_directory,
        ],
    )
