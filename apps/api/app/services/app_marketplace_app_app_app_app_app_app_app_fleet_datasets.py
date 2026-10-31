"""Fleet Datasets — track dataset management platform."""
from __future__ import annotations
def fleet_datasets_status(repos: list[dict]) -> dict:
    active = [r for r in repos if r.get("active", True)]
    datasets = sum(r.get("datasets", 0) for r in repos)
    total_rows = sum(r.get("total_rows", 0) for r in repos)
    return {"repos": len(repos), "active": len(active), "datasets": datasets,
            "total_rows": total_rows, "all_active": len(active) == len(repos)}
