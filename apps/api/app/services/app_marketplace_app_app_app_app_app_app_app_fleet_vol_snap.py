"""Fleet volume snapshots — track volume snapshot freshness."""
from __future__ import annotations
def fleet_vol_snapshots(volumes: list[dict]) -> dict:
    with_snap = [v for v in volumes if v.get("has_snapshot", False)]
    stale = [v for v in volumes if v.get("snapshot_age_hours", 999) > 24]
    return {"total": len(volumes), "with_snapshot": len(with_snap),
            "stale_snapshots": len(stale), "all_fresh": len(stale) == 0}
