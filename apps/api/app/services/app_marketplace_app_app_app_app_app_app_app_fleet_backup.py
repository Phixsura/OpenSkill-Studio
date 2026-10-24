"""Fleet backup status — track backup freshness and success."""
from __future__ import annotations
def fleet_backup_status(backups: list[dict]) -> dict:
    fresh = [b for b in backups if b.get("age_hours", 999) <= 24]
    failed = [b for b in backups if b.get("status") == "failed"]
    return {"total": len(backups), "fresh": len(fresh), "stale": len(backups) - len(fresh),
            "failed": len(failed), "healthy": len(failed) == 0 and len(fresh) == len(backups)}
