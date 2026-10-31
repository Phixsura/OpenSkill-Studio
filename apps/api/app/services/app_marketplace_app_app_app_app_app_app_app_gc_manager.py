"""Garbage collector manager — clean up stale/orphaned resources."""
from __future__ import annotations


def find_garbage(resources: list[dict], max_age_hours: int = 72) -> dict:
    stale = [r for r in resources if r.get("age_hours", 0) > max_age_hours]
    orphaned = [r for r in resources if r.get("orphaned", False)]
    total_size = sum(r.get("size_mb", 0) for r in stale + orphaned)
    return {"stale": len(stale), "orphaned": len(orphaned),
            "total_reclaimable_mb": round(total_size, 1),
            "items": [{"id": r["id"], "type": r.get("type", ""), "size_mb": r.get("size_mb", 0)}
                      for r in stale + orphaned]}


def gc_stats(runs: list[dict]) -> dict:
    total_reclaimed = sum(r.get("reclaimed_mb", 0) for r in runs)
    total_items = sum(r.get("items_cleaned", 0) for r in runs)
    return {"total_runs": len(runs), "total_reclaimed_mb": round(total_reclaimed, 1),
            "total_items_cleaned": total_items}
