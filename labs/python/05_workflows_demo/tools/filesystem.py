"""
tools/filesystem.py
-------------------
Local filesystem tools usable both directly in Python and as function tools
for agents built with the Microsoft Agent Framework (Azure OpenAI Chat agents).

Each function is decorated with @ai_function so it can be registered as a tool.
All use standard Python I/O and are safe for local execution.
"""

import os
import json
import shutil
from typing import Annotated, List
from pathlib import Path

from pydantic import Field
from agent_framework import ai_function


# ---------------------------------------------------------------------
# Helper utilities (non-tool internal helpers)
# ---------------------------------------------------------------------

def _safe_path(path: str) -> Path:
    """Normalize and expand user path safely."""
    return Path(os.path.expanduser(path)).resolve()


def _list_entry_info(entry: Path) -> dict:
    """Return minimal file info for a directory entry."""
    return {
        "name": entry.name,
        "path": str(entry),
        "type": "directory" if entry.is_dir() else "file",
        "size": entry.stat().st_size if entry.is_file() else None,
        "modified": entry.stat().st_mtime,
    }


# ---------------------------------------------------------------------
# Core FileSystem Tools
# ---------------------------------------------------------------------

@ai_function(
    name="create_directory",
    description="Create a new directory or ensure a directory exists."
)
def create_directory(
    path: Annotated[str, Field(description="The directory path to create or ensure exists.")],
) -> str:
    path_obj = _safe_path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return f"Directory ensured: {path_obj}"


@ai_function(
    name="directory_tree",
    description="Get a recursive tree view of files and directories as a JSON structure."
)
def directory_tree(
    path: Annotated[str, Field(description="Root directory to scan recursively.")],
) -> str:
    path_obj = _safe_path(path)

    def _build_tree(p: Path):
        if p.is_dir():
            return {
                "name": p.name,
                "type": "directory",
                "children": [_build_tree(child) for child in sorted(p.iterdir())],
            }
        else:
            return {"name": p.name, "type": "file", "size": p.stat().st_size}

    tree = _build_tree(path_obj)
    return json.dumps(tree, indent=2)


@ai_function(
    name="edit_file",
    description="Make line-based edits to a text file (replace or insert lines)."
)
def edit_file(
    path: Annotated[str, Field(description="The file path to modify.")],
    line_number: Annotated[int, Field(description="1-based line number to replace or insert.")],
    new_content: Annotated[str, Field(description="The new line content to write.")],
) -> str:
    path_obj = _safe_path(path)
    lines = []
    if path_obj.exists():
        lines = path_obj.read_text(encoding="utf-8").splitlines()
    while len(lines) < line_number:
        lines.append("")
    lines[line_number - 1] = new_content
    path_obj.write_text("\n".join(lines), encoding="utf-8")
    return f"Edited line {line_number} in {path_obj}"


@ai_function(
    name="get_file_info",
    description="Retrieve detailed metadata about a file or directory."
)
def get_file_info(
    path: Annotated[str, Field(description="The file or directory path.")],
) -> dict:
    p = _safe_path(path)
    s = p.stat()
    return {
        "path": str(p),
        "type": "directory" if p.is_dir() else "file",
        "size": s.st_size,
        "modified": s.st_mtime,
        "created": s.st_ctime,
        "permissions": oct(s.st_mode),
    }


@ai_function(
    name="list_allowed_directories",
    description="Return the list of directories this agent is allowed to access."
)
def list_allowed_directories() -> list[str]:
    # TODO: adapt this list to your sandbox policy
    allowed = [
        str(Path.home()),
        str(Path.cwd()),
        "X:/mnt" if os.name == "nt" else "/mnt"
    ]
    return allowed


@ai_function(
    name="list_directory",
    description="Get a detailed listing of all files and directories in a specified path."
)
def list_directory(
    path: Annotated[str, Field(description="The directory to list contents of.")],
) -> list[dict]:
    path_obj = _safe_path(path)
    if not path_obj.is_dir():
        raise FileNotFoundError(f"{path_obj} is not a directory")
    return [_list_entry_info(e) for e in sorted(path_obj.iterdir())]


@ai_function(
    name="move_file",
    description="Move or rename a file or directory."
)
def move_file(
    src: Annotated[str, Field(description="The source path to move or rename.")],
    dst: Annotated[str, Field(description="The destination path to move or rename to.")],
) -> str:
    src_p, dst_p = _safe_path(src), _safe_path(dst)
    shutil.move(str(src_p), str(dst_p))
    return f"Moved {src_p} → {dst_p}"


@ai_function(
    name="read_file",
    description="Read the complete contents of a file from the file system."
)
def read_file(
    path: Annotated[str, Field(description="The file path to read.")],
) -> str:
    return _safe_path(path).read_text(encoding="utf-8")


@ai_function(
    name="read_multiple_files",
    description="Read the contents of multiple files simultaneously and return as a dict."
)
def read_multiple_files(
    paths: Annotated[List[str], Field(description="List of file paths to read.")],
) -> dict[str, str]:
    result = {}
    for p in paths:
        path_obj = _safe_path(p)
        if path_obj.is_file():
            result[str(path_obj)] = path_obj.read_text(encoding="utf-8")
    return result


@ai_function(
    name="search_files",
    description="Recursively search for files and directories matching a pattern."
)
def search_files(
    root: Annotated[str, Field(description="Root directory to search recursively.")],
    pattern: Annotated[str, Field(description="Wildcard pattern (e.g. '*.py')")],
) -> list[str]:
    root_p = _safe_path(root)
    matches = [str(p) for p in root_p.rglob(pattern)]
    return matches


@ai_function(
    name="write_file",
    description="Create a new file or completely overwrite an existing file with new content."
)
def write_file(
    path: Annotated[str, Field(description="The file path to write to.")],
    content: Annotated[str, Field(description="The content to write.")],
) -> str:
    p = _safe_path(path)
    os.makedirs(p.parent, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} bytes to {p}"

@ai_function(
    name="get_cwd",
    description="Return the current working directory of the runtime environment."
)
def get_cwd() -> str:
    """Return the absolute current working directory."""
    return str(Path.cwd().resolve())

all_tools = [
        create_directory,
        directory_tree,
        edit_file,
        get_cwd,
        get_file_info,
        list_allowed_directories,
        list_directory,
        move_file,
        read_file,
        read_multiple_files,
        search_files,
        write_file,
    ]