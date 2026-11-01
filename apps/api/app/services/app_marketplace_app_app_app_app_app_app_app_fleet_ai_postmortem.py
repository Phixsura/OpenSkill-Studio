"""Fleet AI Incident Postmortem — track AI-assisted incident analysis."""
from __future__ import annotations
def fleet_ai_postmortem(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    postmortems = sum(s.get("postmortems", 0) for s in systems)
    action_items = sum(s.get("action_items", 0) for s in systems)
    completed_items = sum(s.get("completed", 0) for s in systems)
    completion_rate = round(completed_items / max(action_items, 1) * 100, 1)
    return {"systems": len(systems), "active": len(active), "postmortems": postmortems,
            "action_items": action_items, "completed": completed_items, "completion_rate": completion_rate, "learning": completion_rate > 80}
