"""API migration tracker — track API version migrations."""
from __future__ import annotations


def track_migration(old_version: str, new_version: str, endpoints: list[dict]) -> dict:
    migrated = sum(1 for e in endpoints if e.get("migrated", False))
    total = len(endpoints)
    deprecated = [e["path"] for e in endpoints if not e.get("migrated")]
    return {"from": old_version, "to": new_version, "total": total,
            "migrated": migrated, "remaining": total - migrated,
            "progress_pct": round(migrated / max(total, 1) * 100),
            "deprecated_paths": deprecated[:10], "complete": migrated == total}


def migration_timeline(migrations: list[dict]) -> dict:
    complete = sum(1 for m in migrations if m.get("complete"))
    return {"total": len(migrations), "complete": complete,
            "in_progress": len(migrations) - complete}
