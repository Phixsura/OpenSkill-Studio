"""Fleet AWS ECS — track container service health."""
from __future__ import annotations
def fleet_ecs_status(services: list[dict]) -> dict:
    active = [s for s in services if s.get("status") == "ACTIVE"]
    running_tasks = sum(s.get("running_count", 0) for s in services)
    desired_tasks = sum(s.get("desired_count", 0) for s in services)
    return {"services": len(services), "active": len(active), "running_tasks": running_tasks,
            "desired_tasks": desired_tasks, "stable": running_tasks == desired_tasks}
