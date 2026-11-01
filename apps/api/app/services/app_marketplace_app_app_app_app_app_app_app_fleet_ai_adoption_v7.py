"""Fleet AI Adoption v7 — track AI platform adoption funnel."""
from __future__ import annotations
def fleet_ai_adoption_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    signups = sum(t.get("signups_30d", 0) for t in trackers)
    activated = sum(t.get("activated", 0) for t in trackers)
    retained_30d = sum(t.get("retained", 0) for t in trackers)
    conversion = round(activated / max(signups, 1) * 100, 1)
    return {"trackers": len(trackers), "active": len(active), "signups": signups,
            "activated": activated, "retained": retained_30d, "conversion": conversion, "growing": conversion > 30}
