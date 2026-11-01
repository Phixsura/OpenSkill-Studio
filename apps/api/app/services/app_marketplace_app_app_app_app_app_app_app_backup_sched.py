"""Backup scheduler — manage automated backup schedules."""
from __future__ import annotations
import time
import hashlib


def create_schedule(name: str, frequency: str, retention_days: int = 30,
                    targets: list[str] | None = None) -> dict:
    valid_freq = {"hourly", "daily", "weekly", "monthly"}
    if frequency not in valid_freq:
        return {"created": False, "error": f"invalid_frequency, must be one of {sorted(valid_freq)}"}
    return {"created": True, "name": name, "frequency": frequency,
            "retention_days": retention_days, "targets": targets or ["database"],
            "next_run": _next_run(frequency)}


def _next_run(frequency: str) -> int:
    intervals = {"hourly": 3600, "daily": 86400, "weekly": 604800, "monthly": 2592000}
    return int(time.time()) + intervals.get(frequency, 86400)


def create_backup_record(schedule_name: str, size_mb: float, duration_sec: int) -> dict:
    backup_id = hashlib.sha256(f"{schedule_name}:{time.time()}".encode()).hexdigest()[:12]
    return {"backup_id": backup_id, "schedule": schedule_name,
            "size_mb": round(size_mb, 1), "duration_sec": duration_sec,
            "status": "completed", "timestamp": time.time()}


def summarize_backups(backups: list[dict]) -> dict:
    total_size = sum(b.get("size_mb", 0) for b in backups)
    completed = sum(1 for b in backups if b.get("status") == "completed")
    return {"total": len(backups), "completed": completed,
            "failed": len(backups) - completed,
            "total_size_mb": round(total_size, 1),
            "avg_size_mb": round(total_size / max(len(backups), 1), 1)}
