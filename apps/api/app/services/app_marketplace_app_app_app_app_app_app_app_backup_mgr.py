"""Platform backup manager — schedule and track backups."""
from __future__ import annotations
import time


class BackupManager:
    def __init__(self, retention_days: int = 30):
        self._backups: list[dict] = []
        self._retention = retention_days

    def create_backup(self, name: str, size_mb: float, backup_type: str = "full") -> dict:
        backup = {"name": name, "size_mb": round(size_mb, 2), "type": backup_type,
                  "created_at": time.time(), "status": "completed",
                  "expires_at": time.time() + self._retention * 86400}
        self._backups.append(backup)
        return backup

    def list_backups(self, backup_type: str = "") -> list[dict]:
        if backup_type:
            return [b for b in self._backups if b["type"] == backup_type]
        return list(self._backups)

    def cleanup_expired(self, now: float | None = None) -> dict:
        now = now or time.time()
        before = len(self._backups)
        self._backups = [b for b in self._backups if b["expires_at"] > now]
        removed = before - len(self._backups)
        return {"removed": removed, "remaining": len(self._backups)}

    def stats(self) -> dict:
        total_size = sum(b["size_mb"] for b in self._backups)
        by_type: dict[str, int] = {}
        for b in self._backups:
            by_type[b["type"]] = by_type.get(b["type"], 0) + 1
        return {"total_backups": len(self._backups), "total_size_mb": round(total_size, 2),
                "by_type": by_type, "retention_days": self._retention}
