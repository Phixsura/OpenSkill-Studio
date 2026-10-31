"""Fleet AI Gradient Monitor — track gradient flow and health during training."""
from __future__ import annotations
def fleet_ai_gradient_monitor(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active", True)]
    jobs = sum(m.get("jobs", 0) for m in monitors)
    vanishing = sum(m.get("vanishing", 0) for m in monitors)
    exploding = sum(m.get("exploding", 0) for m in monitors)
    healthy = sum(m.get("healthy", 0) for m in monitors)
    return {"monitors": len(monitors), "active": len(active), "jobs": jobs,
            "vanishing": vanishing, "exploding": exploding, "healthy": healthy, "stable": vanishing == 0 and exploding == 0}
