"""Sandbox File System — virtual filesystem for sandboxed extension execution.

Provides an in-memory filesystem that extensions can read/write within
their sandbox, with size limits and path traversal prevention.
"""
from __future__ import annotations
import posixpath
from dataclasses import dataclass


@dataclass
class VirtualFile:
    path: str
    content: bytes
    is_directory: bool = False
    readable: bool = True
    writable: bool = True


class SandboxFileSystem:
    """In-memory virtual filesystem with security boundaries."""

    def __init__(self, root: str = "/sandbox", max_file_size: int = 1_048_576,
                 max_total_size: int = 10_485_760):
        self._root = root
        self._files: dict[str, VirtualFile] = {}
        self._max_file = max_file_size
        self._max_total = max_total_size
        # Create root directory
        self._files[root] = VirtualFile(root, b"", is_directory=True)

    def _normalize(self, path: str) -> str:
        """Normalize and confine path to sandbox root."""
        if not path.startswith("/"):
            path = posixpath.join(self._root, path)
        normalized = posixpath.normpath(path)
        if not normalized.startswith(self._root):
            raise PermissionError(f"Path traversal denied: {path}")
        return normalized

    def _total_size(self) -> int:
        return sum(len(f.content) for f in self._files.values() if not f.is_directory)

    def write_file(self, path: str, content: bytes | str) -> bool:
        """Write a file to the sandbox filesystem."""
        normalized = self._normalize(path)
        if isinstance(content, str):
            content = content.encode("utf-8")
        if len(content) > self._max_file:
            raise ValueError(f"File exceeds max size: {len(content)} > {self._max_file}")
        new_total = self._total_size() - len(self._files.get(normalized, VirtualFile("", b"")).content) + len(content)
        if new_total > self._max_total:
            raise ValueError("Total filesystem size limit exceeded")
        # Ensure parent directories exist
        parent = posixpath.dirname(normalized)
        if parent != normalized and parent not in self._files:
            self.mkdir(parent)
        self._files[normalized] = VirtualFile(normalized, content)
        return True

    def read_file(self, path: str) -> bytes:
        """Read a file from the sandbox filesystem."""
        normalized = self._normalize(path)
        f = self._files.get(normalized)
        if not f or f.is_directory:
            raise FileNotFoundError(f"File not found: {path}")
        if not f.readable:
            raise PermissionError(f"File not readable: {path}")
        return f.content

    def delete_file(self, path: str) -> bool:
        normalized = self._normalize(path)
        if normalized == self._root:
            raise PermissionError("Cannot delete root")
        return self._files.pop(normalized, None) is not None

    def exists(self, path: str) -> bool:
        return self._normalize(path) in self._files

    def mkdir(self, path: str) -> bool:
        normalized = self._normalize(path)
        if normalized not in self._files:
            self._files[normalized] = VirtualFile(normalized, b"", is_directory=True)
        return True

    def listdir(self, path: str) -> list[str]:
        normalized = self._normalize(path)
        prefix = normalized.rstrip("/") + "/"
        entries = []
        for p in self._files:
            if p.startswith(prefix) and "/" not in p[len(prefix):]:
                entries.append(posixpath.basename(p))
        return sorted(entries)

    def stat(self, path: str) -> dict:
        normalized = self._normalize(path)
        f = self._files.get(normalized)
        if not f:
            raise FileNotFoundError(path)
        return {
            "path": f.path,
            "size": len(f.content),
            "is_directory": f.is_directory,
            "readable": f.readable,
            "writable": f.writable,
        }
