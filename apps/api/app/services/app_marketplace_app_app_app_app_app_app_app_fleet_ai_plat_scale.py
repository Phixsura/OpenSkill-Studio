"""Fleet AI Platform Scalability — track platform scaling capabilities."""
from __future__ import annotations
def fleet_ai_platform_scalability(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    max_rps = sum(t.get("max_rps", 0) for t in trackers)
    current_rps = sum(t.get("current_rps", 0) for t in trackers)
    headroom = round((max_rps - current_rps) / max(max_rps, 1) * 100, 1)
    auto_scale = all(t.get("auto", False) for t in trackers)
    return {"trackers": len(trackers), "active": len(active), "max_rps": max_rps,
            "current_rps": current_rps, "headroom_pct": headroom, "auto_scale": auto_scale, "scalable": headroom > 30}
