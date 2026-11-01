"""Database backup manager — schedule, track, and verify database backups."""
from __future__ import annotations
import secrets
import time


class DbBackupManager:
    def __init__(self):
        self._backups: list[dict] = []

    def create_backup(self, *, database: str, backup_type: str = "full",
                       size_mb: float = 0, now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        bid = f"bak_{secrets.token_hex(6)}"
        backup = {"id": bid, "database": database, "type": backup_type,
                  "size_mb": size_mb, "size_display": f"{size_mb:.1f} MB",
                  "created_at": ts, "status": "completed", "verified": False}
        self._backups.append(backup)
        return {"id": bid, "database": database, "status": "completed"}

    def verify(self, backup_id: str) -> dict:
        b = next((b for b in self._backups if b["id"] == backup_id), None)
        if not b:
            return {"error": "Backup not found"}
        b["verified"] = True
        return {"id": backup_id, "verified": True}

    def latest(self, database: str) -> dict:
        db_backups = [b for b in self._backups if b["database"] == database]
        if not db_backups:
            return {"error": "No backups found"}
        latest = max(db_backups, key=lambda b: b["created_at"])
        return {"id": latest["id"], "type": latest["type"],
                "size_display": latest["size_display"], "verified": latest["verified"]}

    def retention_summary(self) -> dict:
        by_db: dict[str, int] = {}
        total_size = 0.0
        for b in self._backups:
            by_db[b["database"]] = by_db.get(b["database"], 0) + 1
            total_size += b["size_mb"]
        verified = sum(1 for b in self._backups if b["verified"])
        return {"total_backups": len(self._backups), "by_database": by_db,
                "total_size_mb": round(total_size, 1),
                "verified_count": verified, "unverified_count": len(self._backups) - verified}
