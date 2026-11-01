"""Fleet Incident Timeline v9 — track incident lifecycle events."""
from __future__ import annotations
def fleet_incident_timeline_v9(incidents: list[dict]) -> dict:
    detected = sum(1 for i in incidents if i.get("detected"))
    acknowledged = sum(1 for i in incidents if i.get("acknowledged"))
    mitigated = sum(1 for i in incidents if i.get("mitigated"))
    resolved = sum(1 for i in incidents if i.get("resolved"))
    return {"incidents": len(incidents), "detected": detected, "acknowledged": acknowledged,
            "mitigated": mitigated, "resolved": resolved, "healthy": resolved == len(incidents)}
