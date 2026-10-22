"""Sandbox filesystem — virtual filesystem with quotas for sandboxed apps."""

import os


class SandboxFilesystem:
    def __init__(self, *, quota_bytes: int = 50 * 1024 * 1024) -> None:
        self._files: dict[str, bytes] = {}
        self._quota = quota_bytes

    @property
    def used_bytes(self) -> int:
        return sum(len(v) for v in self._files.values())

    def write(self, path: str, content: bytes) -> dict:
        if ".." in path or path.startswith("/"):
            return {"error": "Path traversal not allowed"}
        new_size = self.used_bytes - len(self._files.get(path, b"")) + len(content)
        if new_size > self._quota:
            return {"error": f"Quota exceeded ({new_size} > {self._quota})"}
        self._files[path] = content
        return {"path": path, "size": len(content), "error": None}

    def read(self, path: str) -> bytes | None:
        return self._files.get(path)

    def delete(self, path: str) -> bool:
        return self._files.pop(path, None) is not None

    def list_files(self) -> list[dict]:
        return [{"path": p, "size": len(c)} for p, c in sorted(self._files.items())]

    def stats(self) -> dict:
        return {"files": len(self._files), "used_bytes": self.used_bytes,
                "quota_bytes": self._quota, "usage_pct": round(self.used_bytes / self._quota * 100, 1)}
