"""Fleet AI Incident Timeline — track AI incident chronological analysis."""
from __future__ import annotations
def fleet_ai_incident_timeline(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    incidents_tracked = sum(t.get("incidents", 0) for t in trackers)
    events_recorded = sum(t.get("events", 0) for t in trackers)
    avg_resolution_min = round(sum(t.get("resolution_min", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "incidents": incidents_tracked,
            "events": events_recorded, "resolution_min": avg_resolution_min, "fast": avg_resolution_min < 30}
