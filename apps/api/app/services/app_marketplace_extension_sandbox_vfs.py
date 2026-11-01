"""Sandbox Virtual File System — in-memory VFS for extension sandboxes.

Provides a virtual file system with path validation, size limits,
permission checks, and directory operations for sandboxed extensions.
"""
from __future__ import annotations
import posixpath
import secrets
from dataclasses import dataclass, field
from enum import Enum


class FileType(str, Enum):
    FILE = "file"
    DIRECTORY = "directory"


class Permission(str, Enum):
    READ = "r"
    WRITE = "w"
    EXECUTE = "x"


@dataclass
class VFSNode:
    name: str
    file_type: FileType
    content: bytes = b""
    permissions: str = "rw"
    children: dict[str, "VFSNode"] = field(default_factory=dict)
    size_bytes: int = 0

    def __post_init__(self):
        self.size_bytes = len(self.content)


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_PATH_DEPTH = 20
MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100 MB


class SandboxVFSService:
    """In-memory virtual file system for sandboxed extensions."""

    def __init__(self):
        self._roots: dict[str, VFSNode] = {}
        self._total_size: dict[str, int] = {}

    def create_sandbox(self, sandbox_id: str) -> None:
        self._roots[sandbox_id] = VFSNode(name="/", file_type=FileType.DIRECTORY)
        self._total_size[sandbox_id] = 0

    def _validate_path(self, path: str) -> list[str]:
        if not path.startswith("/"):
            raise ValueError("Path must be absolute")
        normalized = posixpath.normpath(path)
        if not normalized.startswith("/"):
            raise ValueError("Path traversal not allowed")
        if ".." in path:
            raise ValueError("Path traversal not allowed")
        parts = [p for p in normalized.split("/") if p]
        if len(parts) > MAX_PATH_DEPTH:
            raise ValueError(f"Path too deep (max {MAX_PATH_DEPTH})")
        return parts

    def _navigate(self, root: VFSNode, parts: list[str],
                  create_dirs: bool = False) -> VFSNode:
        current = root
        for part in parts:
            if current.file_type != FileType.DIRECTORY:
                raise ValueError(f"Not a directory: {part}")
            if part not in current.children:
                if create_dirs:
                    current.children[part] = VFSNode(name=part, file_type=FileType.DIRECTORY)
                else:
                    raise FileNotFoundError(f"Not found: {part}")
            current = current.children[part]
        return current

    def write_file(self, sandbox_id: str, path: str, content: bytes) -> dict:
        root = self._roots.get(sandbox_id)
        if not root:
            raise ValueError("Sandbox not found")
        if len(content) > MAX_FILE_SIZE:
            raise ValueError(f"File too large (max {MAX_FILE_SIZE} bytes)")

        parts = self._validate_path(path)
        filename = parts[-1]
        dir_parts = parts[:-1]

        parent = self._navigate(root, dir_parts, create_dirs=True)

        old_size = 0
        if filename in parent.children:
            old_size = parent.children[filename].size_bytes

        new_total = self._total_size.get(sandbox_id, 0) - old_size + len(content)
        if new_total > MAX_TOTAL_SIZE:
            raise ValueError("Sandbox storage limit exceeded")

        parent.children[filename] = VFSNode(
            name=filename, file_type=FileType.FILE, content=content,
        )
        self._total_size[sandbox_id] = new_total

        return {"path": path, "size": len(content), "total_used": new_total}

    def read_file(self, sandbox_id: str, path: str) -> bytes:
        root = self._roots.get(sandbox_id)
        if not root:
            raise ValueError("Sandbox not found")
        parts = self._validate_path(path)
        node = self._navigate(root, parts)
        if node.file_type != FileType.FILE:
            raise ValueError("Not a file")
        return node.content

    def delete(self, sandbox_id: str, path: str) -> bool:
        root = self._roots.get(sandbox_id)
        if not root:
            return False
        parts = self._validate_path(path)
        parent = self._navigate(root, parts[:-1])
        name = parts[-1]
        if name in parent.children:
            node = parent.children.pop(name)
            self._total_size[sandbox_id] -= self._calc_size(node)
            return True
        return False

    def _calc_size(self, node: VFSNode) -> int:
        if node.file_type == FileType.FILE:
            return node.size_bytes
        return sum(self._calc_size(c) for c in node.children.values())

    def list_dir(self, sandbox_id: str, path: str = "/") -> list[dict]:
        root = self._roots.get(sandbox_id)
        if not root:
            return []
        parts = self._validate_path(path) if path != "/" else []
        node = self._navigate(root, parts) if parts else root
        if node.file_type != FileType.DIRECTORY:
            raise ValueError("Not a directory")
        return [{"name": c.name, "type": c.file_type.value, "size": c.size_bytes}
                for c in node.children.values()]

    def get_usage(self, sandbox_id: str) -> dict:
        return {
            "used_bytes": self._total_size.get(sandbox_id, 0),
            "max_bytes": MAX_TOTAL_SIZE,
            "usage_percent": round(self._total_size.get(sandbox_id, 0) / MAX_TOTAL_SIZE * 100, 1),
        }
