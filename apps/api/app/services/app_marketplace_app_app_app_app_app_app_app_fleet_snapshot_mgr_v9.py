"""Fleet Snapshot Manager v9 — track volume snapshot lifecycle."""
from __future__ import annotations
def fleet_snapshot_mgr_v9(snapshots: list[dict]) -> dict:
    available = [s for s in snapshots if s.get("status") == "available"]
    size_gb = sum(s.get("size_gb", 0) for s in snapshots)
    stale = [s for s in snapshots if s.get("age_days", 0) > 30]
    return {"total": len(snapshots), "available": len(available), "size_gb": round(size_gb, 1),
            "stale": len(stale), "healthy": len(stale) == 0}
