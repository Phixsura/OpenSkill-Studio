"""Fleet incident communication — track stakeholder notification metrics."""
from __future__ import annotations
def fleet_incident_comms(incidents: list[dict]) -> dict:
    notified = [i for i in incidents if i.get("stakeholders_notified", False)]
    avg_notify_min = round(sum(i.get("notify_time_min", 0) for i in notified) / max(len(notified), 1), 1)
    return {"total": len(incidents), "notified": len(notified),
            "not_notified": len(incidents) - len(notified),
            "avg_notify_min": avg_notify_min, "timely": avg_notify_min <= 15}
