"""Fleet Sanity — track structured content platform."""
from __future__ import annotations
def fleet_sanity_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    documents = sum(p.get("documents", 0) for p in projects)
    datasets = sum(p.get("datasets", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "documents": documents,
            "datasets": datasets, "all_active": len(active) == len(projects)}
