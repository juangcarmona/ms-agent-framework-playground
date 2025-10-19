# agents/dev_helper_agent.py
from agent_framework import ChatAgent
from tools.development import (
    create_project_structure,
    insert_code_snippet,
    run_python_script,
    lint_code,
    run_tests,
)

def build_dev_helper_agent(chat_client):
    """
    Agent that helps with development tasks — creates folders, inserts code, runs, and tests.
    """
    return ChatAgent(
        name="DevHelperAgent",
        description="Creates and executes Python projects locally.",
        instructions=(
            "You are a coding assistant with local development capabilities.\n"
            "You can:\n"
            "- Create new project structures.\n"
            "- Insert or modify Python files.\n"
            "- Run code or tests.\n"
            "- Lint files for issues.\n"
            "Always explain what you did and summarize output clearly."
        ),
        chat_client=chat_client,
        tools=[
            create_project_structure,
            insert_code_snippet,
            run_python_script,
            lint_code,
            run_tests,
        ],
    )
