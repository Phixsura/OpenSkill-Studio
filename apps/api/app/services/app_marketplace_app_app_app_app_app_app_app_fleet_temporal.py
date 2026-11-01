"""Fleet Temporal — track durable workflow execution."""
from __future__ import annotations
def fleet_temporal_status(namespaces: list[dict]) -> dict:
    healthy = [n for n in namespaces if n.get("healthy", True)]
    running_workflows = sum(n.get("running_workflows", 0) for n in namespaces)
    completed_24h = sum(n.get("completed_24h", 0) for n in namespaces)
    return {"namespaces": len(namespaces), "healthy": len(healthy), "running_workflows": running_workflows,
            "completed_24h": completed_24h, "all_healthy": len(healthy) == len(namespaces)}
