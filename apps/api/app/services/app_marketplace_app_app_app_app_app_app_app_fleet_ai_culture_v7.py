"""Fleet AI Culture v7 — track engineering culture and developer experience."""
from __future__ import annotations
def fleet_ai_culture_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    enps = round(sum(t.get("enps", 0) for t in trackers) / max(len(trackers), 1))
    dx_score = round(sum(t.get("dx", 0) for t in trackers) / max(len(trackers), 1), 1)
    hackathons = sum(t.get("hackathons", 0) for t in trackers)
    return {"trackers": len(trackers), "active": len(active), "enps": enps,
            "dx_score": dx_score, "hackathons": hackathons, "thriving": enps > 50}
