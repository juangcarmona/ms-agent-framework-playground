"""
tools/system.py
---------------
System-level tools exposing environment, process, and diagnostic capabilities
to an AI agent.  Compatible with Microsoft Agent Framework's @ai_function.
"""

import os
import platform
import socket
import subprocess
import datetime
import json
import getpass

import psutil       # pip install psutil
try:
    import GPUtil   # optional GPU info
except ImportError:
    GPUtil = None

import pkg_resources

from typing import Annotated, Optional
from pydantic import Field
from agent_framework import ai_function


# ---------------------------------------------------------------------
# Core system info
# ---------------------------------------------------------------------

@ai_function(
    name="get_system_info",
    description="Retrieve general information about the operating system and Python runtime."
)
def get_system_info() -> dict:
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "hostname": socket.gethostname(),
        "cwd": os.getcwd(),
    }


@ai_function(
    name="get_user_info",
    description="Get information about the current logged-in user."
)
def get_user_info() -> dict:
    return {
        "username": getpass.getuser(),
        "home": os.path.expanduser("~"),
        "uid": os.getuid() if hasattr(os, "getuid") else None,
    }


@ai_function(
    name="get_hardware_info",
    description="Retrieve basic hardware information (CPU, memory, GPUs if available)."
)
def get_hardware_info() -> dict:
    gpus = [gpu.name for gpu in GPUtil.getGPUs()] if GPUtil else []
    vm = psutil.virtual_memory()
    return {
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory_total": vm.total,
        "memory_available": vm.available,
        "gpus": gpus,
    }


@ai_function(
    name="get_disk_usage",
    description="Get total, used, and free disk space for the given path."
)
def get_disk_usage(
    path: Annotated[str, Field(description="Path to check disk usage for.")] = "."
) -> dict:
    usage = psutil.disk_usage(path)
    return {
        "path": os.path.abspath(path),
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "percent": usage.percent,
    }


@ai_function(
    name="list_env_vars",
    description="List all environment variables and their values."
)
def list_env_vars() -> dict:
    return dict(os.environ)


@ai_function(
    name="get_env_var",
    description="Get a specific environment variable by name."
)
def get_env_var(
    name: Annotated[str, Field(description="Name of the environment variable to retrieve.")]
) -> Optional[str]:
    return os.getenv(name)


# ---------------------------------------------------------------------
# Process & command execution
# ---------------------------------------------------------------------

@ai_function(
    name="run_command",
    description="Execute a shell command and capture its output."
)
def run_command(
    command: Annotated[str, Field(description="The command to execute in the system shell.")],
    cwd: Annotated[Optional[str], Field(description="Optional working directory.")] = None,
    timeout: Annotated[Optional[int], Field(description="Optional timeout in seconds.")] = None,
) -> dict:
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "command": command,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {timeout}s"}


@ai_function(
    name="list_processes",
    description="List running processes with their PID, name, and CPU usage."
)
def list_processes(
    limit: Annotated[int, Field(description="Maximum number of processes to list.")] = 20
) -> list[dict]:
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent"]):
        procs.append(p.info)
        if len(procs) >= limit:
            break
    return procs


@ai_function(
    name="terminate_process",
    description="Terminate a process by its PID."
)
def terminate_process(
    pid: Annotated[int, Field(description="Process ID (PID) to terminate.")]
) -> str:
    try:
        psutil.Process(pid).terminate()
        return f"Terminated process {pid}"
    except Exception as e:
        return f"Failed to terminate {pid}: {e}"


# ---------------------------------------------------------------------
# Network & time
# ---------------------------------------------------------------------

@ai_function(
    name="get_network_info",
    description="Get local IP addresses and network interface information."
)
def get_network_info() -> dict:
    addrs = psutil.net_if_addrs()
    info: dict[str, list[str]] = {}
    for iface, entries in addrs.items():
        info[iface] = [a.address for a in entries if a.family == socket.AF_INET]
    return info


@ai_function(
    name="get_time",
    description="Return the current system date and time in ISO format."
)
def get_time() -> str:
    return datetime.datetime.now().isoformat()


@ai_function(
    name="get_uptime",
    description="Return the system uptime in seconds."
)
def get_uptime() -> float:
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    return (datetime.datetime.now() - boot).total_seconds()


@ai_function(
    name="list_python_packages",
    description="List installed Python packages and versions in the current environment."
)
def list_python_packages() -> dict:
    return {d.project_name: d.version for d in pkg_resources.working_set}
