"""Fleet AI DX v8 — track ultimate developer experience."""
from __future__ import annotations
def fleet_ai_dx_v8(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    nps = round(sum(t.get("nps", 0) for t in trackers) / max(len(trackers), 1))
    ttfv = round(sum(t.get("ttfv_min", 0) for t in trackers) / max(len(trackers), 1), 1)
    satisfaction = round(sum(t.get("sat_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "nps": nps,
            "ttfv": ttfv, "satisfaction": satisfaction, "world_class": nps > 70}
