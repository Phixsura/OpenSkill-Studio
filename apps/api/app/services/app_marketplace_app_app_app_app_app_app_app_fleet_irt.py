"""Fleet incident response time — measure time to acknowledge."""
from __future__ import annotations
def fleet_incident_response(incidents: list[dict]) -> dict:
    times = [i.get("ack_minutes", 0) for i in incidents]
    avg = round(sum(times) / max(len(times), 1), 1)
    within_sla = [t for t in times if t <= 15]
    return {"total": len(incidents), "avg_ack_min": avg,
            "within_sla": len(within_sla), "sla_pct": round(len(within_sla) / max(len(incidents), 1) * 100, 1)}
