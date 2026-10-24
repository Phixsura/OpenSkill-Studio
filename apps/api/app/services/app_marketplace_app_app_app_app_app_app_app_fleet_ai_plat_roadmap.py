"""Fleet AI Platform Roadmap — track AI platform feature roadmap."""
from __future__ import annotations
def fleet_ai_platform_roadmap(roadmaps: list[dict]) -> dict:
    active = [r for r in roadmaps if r.get("active", True)]
    features_planned = sum(r.get("planned", 0) for r in roadmaps)
    in_progress = sum(r.get("in_progress", 0) for r in roadmaps)
    completed = sum(r.get("completed", 0) for r in roadmaps)
    return {"roadmaps": len(roadmaps), "active": len(active), "planned": features_planned,
            "in_progress": in_progress, "completed": completed, "executing": in_progress > 0}
