"""Fleet Neon — track serverless Postgres health."""
from __future__ import annotations
def fleet_neondb_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    compute_hours = sum(p.get("compute_hours_24h", 0) for p in projects)
    branches = sum(p.get("branches", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "compute_hours_24h": round(compute_hours, 1),
            "branches": branches, "serverless": True}
