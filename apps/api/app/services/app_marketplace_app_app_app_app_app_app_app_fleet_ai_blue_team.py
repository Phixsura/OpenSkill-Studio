"""Fleet AI Blue Teaming — track defensive AI security operations."""
from __future__ import annotations
def fleet_ai_blue_teaming(teams: list[dict]) -> dict:
    active = [t for t in teams if t.get("active", True)]
    incidents_handled = sum(t.get("incidents", 0) for t in teams)
    detections_24h = sum(t.get("detections_24h", 0) for t in teams)
    response_time_min = round(sum(t.get("response_min", 0) for t in teams) / max(len(teams), 1), 1)
    return {"teams": len(teams), "active": len(active), "incidents": incidents_handled,
            "detections_24h": detections_24h, "response_min": response_time_min, "defensive": response_time_min < 15}
