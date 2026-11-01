"""Fleet Jenkins — track Jenkins controller and agent health."""
from __future__ import annotations
def fleet_jenkins_status(controllers: list[dict]) -> dict:
    online = [c for c in controllers if c.get("online", True)]
    total_agents = sum(c.get("agents", 0) for c in controllers)
    queue_size = sum(c.get("queue_size", 0) for c in controllers)
    return {"controllers": len(controllers), "online": len(online), "agents": total_agents,
            "queue_size": queue_size, "healthy": len(online) == len(controllers) and queue_size < 50}
