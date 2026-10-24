"""Fleet Octant — track cluster visualization usage."""
from __future__ import annotations
def fleet_octant_usage(sessions: list[dict]) -> dict:
    active = [s for s in sessions if s.get("active", False)]
    clusters_viewed = len(set(s.get("cluster", "") for s in active))
    return {"total_sessions": len(sessions), "active": len(active),
            "clusters_viewed": clusters_viewed, "adopted": len(active) > 5}
