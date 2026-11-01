"""Fleet Incident Response v9 — track incident response team readiness."""
from __future__ import annotations
def fleet_incident_response_v9(teams: list[dict]) -> dict:
    on_call = [t for t in teams if t.get("on_call")]
    avg_ack_time = sum(t.get("avg_ack_min", 0) for t in teams) / len(teams) if teams else 0
    runbooks_ready = sum(1 for t in teams if t.get("runbook_ready"))
    return {"teams": len(teams), "on_call": len(on_call), "avg_ack_min": round(avg_ack_time, 1),
            "runbooks_ready": runbooks_ready, "healthy": len(on_call) == len(teams)}
