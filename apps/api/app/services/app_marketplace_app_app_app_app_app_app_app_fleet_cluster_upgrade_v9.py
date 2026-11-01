"""Fleet Cluster Upgrade v9 — track cluster rolling upgrade progress."""
from __future__ import annotations
def fleet_cluster_upgrade_v9(clusters: list[dict]) -> dict:
    upgraded = [c for c in clusters if c.get("upgraded")]
    in_progress = [c for c in clusters if c.get("upgrading")]
    pending = [c for c in clusters if c.get("pending")]
    return {"clusters": len(clusters), "upgraded": len(upgraded), "in_progress": len(in_progress),
            "pending": len(pending), "healthy": len(pending) == 0}
