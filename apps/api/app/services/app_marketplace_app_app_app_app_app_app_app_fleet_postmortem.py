"""Fleet postmortem tracker — track incident postmortem completion."""
from __future__ import annotations
def fleet_postmortem_status(incidents: list[dict]) -> dict:
    with_pm = [i for i in incidents if i.get("postmortem_done", False)]
    with_actions = [i for i in incidents if i.get("actions_completed", False)]
    return {"total": len(incidents), "postmortems_done": len(with_pm),
            "actions_completed": len(with_actions),
            "completion_pct": round(len(with_pm) / max(len(incidents), 1) * 100, 1)}
