"""Fleet Hygraph — track federated content platform."""
from __future__ import annotations
def fleet_hygraph_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    models = sum(p.get("models", 0) for p in projects)
    entries = sum(p.get("entries", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "models": models,
            "entries": entries, "all_active": len(active) == len(projects)}
