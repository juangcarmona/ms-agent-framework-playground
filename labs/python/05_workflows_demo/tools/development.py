"""
tools/development.py
--------------------
Developer-oriented tools that let an AI agent create, modify, build, and
inspect code projects locally.  Compatible with @ai_function.
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import Annotated, Optional

from pydantic import Field
from agent_framework import ai_function


# ---------------------------------------------------------------------
# Project & environment utilities
# ---------------------------------------------------------------------

@ai_function(
    name="create_project_structure",
    description="Create a basic project folder structure with optional subfolders."
)
def create_project_structure(
    root: Annotated[str, Field(description="Root folder for the new project.")],
    subfolders: Annotated[list[str], Field(description="Subfolders to create under the root.")]=("src","tests","docs"),
) -> str:
    root_path = Path(root).resolve()
    root_path.mkdir(parents=True, exist_ok=True)
    for sf in subfolders:
        (root_path / sf).mkdir(parents=True, exist_ok=True)
    return f"Created project at {root_path} with subfolders {list(subfolders)}"


@ai_function(
    name="initialize_git_repo",
    description="Initialize a new Git repository in the specified directory."
)
def initialize_git_repo(
    path: Annotated[str, Field(description="Directory path for initializing the repository.")],
) -> str:
    result = subprocess.run(["git", "init", path], capture_output=True, text=True)
    return result.stdout or result.stderr


@ai_function(
    name="pip_install",
    description="Install a Python package using pip."
)
def pip_install(
    package: Annotated[str, Field(description="Package name or requirement specifier.")],
) -> str:
    result = subprocess.run(["pip", "install", package], capture_output=True, text=True)
    return result.stdout or result.stderr


@ai_function(
    name="list_dependencies",
    description="List installed dependencies in the current Python environment (pip freeze)."
)
def list_dependencies() -> str:
    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
    return result.stdout.strip()


# ---------------------------------------------------------------------
# Code editing & inspection
# ---------------------------------------------------------------------

@ai_function(
    name="insert_code_snippet",
    description="Append or insert a code snippet into an existing file."
)
def insert_code_snippet(
    path: Annotated[str, Field(description="Path to the target code file.")],
    code: Annotated[str, Field(description="Code snippet to insert.")],
    append: Annotated[bool, Field(description="If True, append at end; otherwise insert at top.")]=True,
) -> str:
    p = Path(path).resolve()
    existing = p.read_text(encoding="utf-8") if p.exists() else ""
    new_content = existing + "\n" + code if append else code + "\n" + existing
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(new_content, encoding="utf-8")
    return f"Inserted code into {p}"


@ai_function(
    name="run_python_script",
    description="Execute a Python script and capture its output."
)
def run_python_script(
    path: Annotated[str, Field(description="Path to the Python script to execute.")],
    args: Annotated[Optional[str], Field(description="Optional arguments to pass to the script.")] = None,
) -> dict:
    cmd = ["python", path] + (args.split() if args else [])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "command": " ".join(cmd),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


@ai_function(
    name="run_tests",
    description="Run unit tests using pytest if available."
)
def run_tests(
    path: Annotated[str, Field(description="Directory or test file path to run tests for.")] = "tests",
) -> dict:
    cmd = ["pytest", path, "--maxfail=3", "-q"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


@ai_function(
    name="lint_code",
    description="Run pylint or flake8 on a Python file or directory."
)
def lint_code(
    path: Annotated[str, Field(description="Target file or directory to lint.")],
) -> str:
    # Try pylint first; fall back to flake8 if missing.
    tool = shutil.which("pylint") or shutil.which("flake8")
    if not tool:
        return "No linter (pylint/flake8) installed."
    result = subprocess.run([tool, path], capture_output=True, text=True)
    return result.stdout or result.stderr


@ai_function(
    name="summarize_codebase",
    description="Count files, lines of code, and summarize language distribution."
)
def summarize_codebase(
    root: Annotated[str, Field(description="Root directory of the codebase.")]="."
) -> dict:
    summary: dict[str, dict[str, int]] = {}
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if not ext:
                continue
            path = os.path.join(dirpath, f)
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    lines = sum(1 for _ in fh)
            except Exception:
                lines = 0
            summary.setdefault(ext, {"files": 0, "lines": 0})
            summary[ext]["files"] += 1
            summary[ext]["lines"] += lines
    total_lines = sum(v["lines"] for v in summary.values())
    return {"languages": summary, "total_lines": total_lines}
