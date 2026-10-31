"""Fleet AI Agents — track autonomous AI agent deployments."""
from __future__ import annotations
def fleet_ai_agents_status(agents: list[dict]) -> dict:
    running = [a for a in agents if a.get("running", True)]
    tasks_completed = sum(a.get("tasks_completed_24h", 0) for a in agents)
    tools_used = sum(a.get("tools_available", 0) for a in agents)
    return {"agents": len(agents), "running": len(running), "tasks_24h": tasks_completed,
            "tools": tools_used, "all_running": len(running) == len(agents)}
