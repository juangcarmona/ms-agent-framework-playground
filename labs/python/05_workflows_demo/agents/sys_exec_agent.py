# agents/sys_exec_agent.py
from agent_framework import ChatAgent
from tools.system import run_command, list_processes

def build_sys_exec_agent(chat_client):
    return ChatAgent(
        name="SysExecAgent",
        description="Executes shell commands and reports results.",
        instructions=(
            "You are a controlled command execution agent.\n"
            "Use 'run_command' for safe shell execution (pwd, ls, python, etc.).\n"
            "You can also use 'list_processes' to see what's running."
        ),
        chat_client=chat_client,
        tools=[run_command, list_processes],
    )
