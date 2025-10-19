# agents/system_inspector_agent.py
from agent_framework import ChatAgent
from tools.system import (
    get_system_info,
    get_user_info,
    get_hardware_info,
    get_disk_usage,
    get_network_info,
)

def build_system_inspector_agent(chat_client):
    """
    Agent that inspects the local machine and reports system diagnostics.
    """
    return ChatAgent(
        name="SystemInspectorAgent",
        description="Inspects the system environment and produces summaries or reports.",
        instructions=(
            "You are a diagnostic assistant with access to system tools.\n"
            "Use the provided tools to:\n"
            "- Retrieve general OS and hardware info.\n"
            "- List network interfaces and disk usage.\n"
            "- When asked for 'system status' or 'environment summary', combine these results.\n"
            "Always return information as clean Markdown sections."
        ),
        chat_client=chat_client,
        tools=[
            get_system_info,
            get_user_info,
            get_hardware_info,
            get_disk_usage,
            get_network_info,
        ],
    )
