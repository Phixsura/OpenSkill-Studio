"""Fleet sprint velocity — track sprint-over-sprint velocity."""
from __future__ import annotations
def fleet_sprint_velocity(sprints: list[dict]) -> dict:
    points = [s.get("completed_points", 0) for s in sprints]
    avg = round(sum(points) / max(len(points), 1), 1)
    trend = "improving" if len(points) >= 2 and points[-1] > points[0] else "stable"
    return {"sprints": len(sprints), "avg_velocity": avg, "latest": points[-1] if points else 0, "trend": trend}
