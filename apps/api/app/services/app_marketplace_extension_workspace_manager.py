"""Workspace Manager — manage developer workspaces for extension development.

Creates isolated workspaces with project files, dependencies, build
configs, and collaborative editing support.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class WorkspaceStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    BUILDING = "building"
    ERROR = "error"


@dataclass
class WorkspaceFile:
    path: str
    content: str
    language: str = ""
    size_bytes: int = 0

    def __post_init__(self):
        self.size_bytes = len(self.content.encode())
        if not self.language:
            ext = self.path.rsplit(".", 1)[-1] if "." in self.path else ""
            lang_map = {"ts": "typescript", "js": "javascript", "py": "python",
                        "json": "json", "md": "markdown", "yaml": "yaml", "yml": "yaml"}
            self.language = lang_map.get(ext, "text")


@dataclass
class Workspace:
    workspace_id: str
    extension_id: str
    owner_id: str
    name: str
    status: WorkspaceStatus = WorkspaceStatus.ACTIVE
    files: dict[str, WorkspaceFile] = field(default_factory=dict)
    collaborators: set[str] = field(default_factory=set)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class WorkspaceManagerService:
    """Manages developer workspaces for extension building."""

    MAX_FILES_PER_WORKSPACE = 200
    MAX_FILE_SIZE = 1024 * 1024  # 1MB

    def __init__(self):
        self._workspaces: dict[str, Workspace] = {}

    def create(self, extension_id: str, owner_id: str,
               name: str) -> Workspace:
        ws_id = f"ws_{secrets.token_urlsafe(10)}"
        ws = Workspace(
            workspace_id=ws_id, extension_id=extension_id,
            owner_id=owner_id, name=name,
        )
        self._workspaces[ws_id] = ws
        return ws

    def add_file(self, workspace_id: str, path: str, content: str,
                 caller_id: str) -> WorkspaceFile | dict:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return {"error": "Workspace not found"}
        if not caller_id or (caller_id != ws.owner_id and caller_id not in ws.collaborators):
            return {"error": "Not authorized"}
        if len(content.encode()) > self.MAX_FILE_SIZE:
            return {"error": "File too large"}
        if path not in ws.files and len(ws.files) >= self.MAX_FILES_PER_WORKSPACE:
            return {"error": "Too many files"}
        if ".." in path:
            return {"error": "Path traversal not allowed"}

        f = WorkspaceFile(path=path, content=content)
        ws.files[path] = f
        return f

    def get_file(self, workspace_id: str, path: str, caller_id: str = "") -> str | None:
        ws = self._workspaces.get(workspace_id)
        if not ws or path not in ws.files:
            return None
        if caller_id and caller_id != ws.owner_id and caller_id not in ws.collaborators:
            return None
        return ws.files[path].content

    def delete_file(self, workspace_id: str, path: str, caller_id: str = "") -> bool:
        ws = self._workspaces.get(workspace_id)
        if not ws or path not in ws.files:
            return False
        if caller_id and caller_id != ws.owner_id:
            return False
        del ws.files[path]
        return True

    def add_collaborator(self, workspace_id: str, user_id: str,
                         caller_id: str) -> bool:
        ws = self._workspaces.get(workspace_id)
        if not ws or ws.owner_id != caller_id:
            return False
        ws.collaborators.add(user_id)
        return True

    def list_files(self, workspace_id: str) -> list[dict]:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return []
        return [{"path": f.path, "language": f.language, "size": f.size_bytes}
                for f in ws.files.values()]

    def archive(self, workspace_id: str, caller_id: str) -> bool:
        ws = self._workspaces.get(workspace_id)
        if not ws or ws.owner_id != caller_id:
            return False
        ws.status = WorkspaceStatus.ARCHIVED
        return True

    def list_workspaces(self, owner_id: str) -> list[Workspace]:
        return [ws for ws in self._workspaces.values()
                if ws.owner_id == owner_id or owner_id in ws.collaborators]
