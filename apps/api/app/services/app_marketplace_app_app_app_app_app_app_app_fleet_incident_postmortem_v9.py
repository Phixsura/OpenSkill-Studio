"""Fleet Incident Postmortem v9 — track incident reviews and action items."""
from __future__ import annotations
def fleet_incident_postmortem_v9(postmortems: list[dict]) -> dict:
    completed = [p for p in postmortems if p.get("completed")]
    action_items = sum(p.get("action_items", 0) for p in postmortems)
    resolved_actions = sum(p.get("resolved_actions", 0) for p in postmortems)
    return {"total": len(postmortems), "completed": len(completed), "action_items": action_items,
            "resolved_actions": resolved_actions, "healthy": resolved_actions >= action_items * 0.8}
