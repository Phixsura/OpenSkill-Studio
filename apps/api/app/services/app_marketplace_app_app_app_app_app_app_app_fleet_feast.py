"""Fleet Feast — track ML feature store platform."""
from __future__ import annotations
def fleet_feast_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    feature_views = sum(p.get("feature_views", 0) for p in projects)
    entities = sum(p.get("entities", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "feature_views": feature_views,
            "entities": entities, "all_active": len(active) == len(projects)}
