"""Fleet Appwrite — track open-source BaaS platform."""
from __future__ import annotations
def fleet_appwrite_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    databases = sum(p.get("databases", 0) for p in projects)
    storage_gb = sum(p.get("storage_gb", 0) for p in projects)
    functions = sum(p.get("functions", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "databases": databases,
            "storage_gb": round(storage_gb, 1), "functions": functions}
