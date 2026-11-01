"""Fleet ConfigMap usage — track configmap sizes and staleness."""
from __future__ import annotations
def fleet_configmap_usage(maps: list[dict]) -> dict:
    total_bytes = sum(m.get("size_bytes", 0) for m in maps)
    oversized = [m for m in maps if m.get("size_bytes", 0) > 1048576]
    stale = [m for m in maps if m.get("age_days", 0) > 90]
    return {"total": len(maps), "total_bytes": total_bytes, "oversized": len(oversized),
            "stale": len(stale), "clean": len(oversized) == 0 and len(stale) == 0}
