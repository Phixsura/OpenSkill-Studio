"""Fleet PagerDuty — track incident management metrics."""
from __future__ import annotations
def fleet_pagerduty_status(services: list[dict]) -> dict:
    active_incidents = sum(s.get("active_incidents", 0) for s in services)
    acknowledged = sum(s.get("acknowledged", 0) for s in services)
    avg_ack_min = round(sum(s.get("avg_ack_min", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "active_incidents": active_incidents,
            "acknowledged": acknowledged, "avg_ack_min": avg_ack_min, "calm": active_incidents == 0}
