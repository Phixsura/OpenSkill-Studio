"""Fleet AI Roadmap v7 — track platform feature roadmap execution."""
from __future__ import annotations
def fleet_ai_roadmap_v7(roadmaps: list[dict]) -> dict:
    active = [r for r in roadmaps if r.get("active", True)]
    features_planned = sum(r.get("planned", 0) for r in roadmaps)
    in_progress = sum(r.get("in_progress", 0) for r in roadmaps)
    shipped = sum(r.get("shipped", 0) for r in roadmaps)
    on_time_pct = round(sum(r.get("on_time_pct", 0) for r in roadmaps) / max(len(roadmaps), 1), 1)
    return {"roadmaps": len(roadmaps), "active": len(active), "planned": features_planned,
            "in_progress": in_progress, "shipped": shipped, "on_time": on_time_pct, "executing": on_time_pct > 80}
