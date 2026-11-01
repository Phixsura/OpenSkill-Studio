"""Fleet CrewAI — track AI agent orchestration."""
from __future__ import annotations
def fleet_crewai_status(crews: list[dict]) -> dict:
    active = [c for c in crews if c.get("active", True)]
    agents = sum(c.get("agents", 0) for c in crews)
    tasks_completed = sum(c.get("tasks_completed_24h", 0) for c in crews)
    return {"crews": len(crews), "active": len(active), "agents": agents,
            "tasks_completed_24h": tasks_completed, "productive": tasks_completed > 0}
