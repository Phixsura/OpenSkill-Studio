"""Database migration status — track applied and pending migrations."""
from __future__ import annotations


def check_migration_status(applied: list[dict], available: list[dict]) -> dict:
    applied_ids = {m["id"] for m in applied}
    pending = [m for m in available if m["id"] not in applied_ids]
    latest = applied[-1]["id"] if applied else None
    return {"applied": len(applied), "pending": len(pending), "total": len(available),
            "latest_applied": latest, "pending_migrations": pending,
            "up_to_date": len(pending) == 0,
            "has_destructive": any(m.get("destructive", False) for m in pending)}


def estimate_migration_time(pending: list[dict]) -> dict:
    total_sec = sum(m.get("estimated_sec", 5) for m in pending)
    needs_downtime = any(m.get("requires_lock", False) for m in pending)
    return {"pending_count": len(pending), "estimated_sec": total_sec,
            "estimated_display": f"{total_sec // 60}m {total_sec % 60}s",
            "needs_downtime": needs_downtime}
