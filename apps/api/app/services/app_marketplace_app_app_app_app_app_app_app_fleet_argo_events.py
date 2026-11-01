"""Fleet Argo Events — track event-driven automation."""
from __future__ import annotations
def fleet_argo_events(sources: list[dict]) -> dict:
    active = [s for s in sources if s.get("active", True)]
    total_triggered = sum(s.get("triggers_24h", 0) for s in sources)
    failed_triggers = sum(s.get("failed_triggers", 0) for s in sources)
    return {"total": len(sources), "active": len(active), "triggers_24h": total_triggered,
            "failed": failed_triggers, "reliable": failed_triggers == 0}
