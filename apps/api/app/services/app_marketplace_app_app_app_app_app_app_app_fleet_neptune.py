"""Fleet Neptune — track ML experiment tracking."""
from __future__ import annotations
def fleet_neptune_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    runs = sum(p.get("runs", 0) for p in projects)
    storage_gb = sum(p.get("storage_gb", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "runs": runs,
            "storage_gb": round(storage_gb, 1), "all_active": len(active) == len(projects)}
