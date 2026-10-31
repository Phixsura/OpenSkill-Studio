"""Fleet AI Platform Adoption — track enterprise AI platform adoption funnel."""
from __future__ import annotations
def fleet_ai_platform_adoption(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    signups = sum(t.get("signups_24h", 0) for t in trackers)
    activated = sum(t.get("activated", 0) for t in trackers)
    retained = sum(t.get("retained", 0) for t in trackers)
    conversion = round(activated / max(signups, 1) * 100, 1)
    return {"trackers": len(trackers), "active": len(active), "signups": signups,
            "activated": activated, "retained": retained, "conversion": conversion, "growing": conversion > 20}
