"""Fleet Argo WF Events — track workflow event triggers."""
from __future__ import annotations
def fleet_argo_wf_events(events: list[dict]) -> dict:
    triggered = [e for e in events if e.get("triggered_workflow", False)]
    total_triggers = len(triggered)
    return {"total_events": len(events), "triggered_workflows": total_triggers,
            "trigger_rate": round(total_triggers / max(len(events), 1) * 100, 1)}
