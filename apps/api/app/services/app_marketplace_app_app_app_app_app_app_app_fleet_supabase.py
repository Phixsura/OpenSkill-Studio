"""Fleet Supabase — track BaaS platform health."""
from __future__ import annotations
def fleet_supabase_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("status") == "ACTIVE_HEALTHY"]
    db_size_gb = sum(p.get("db_size_gb", 0) for p in projects)
    api_requests = sum(p.get("api_requests_24h", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "db_size_gb": round(db_size_gb, 1),
            "api_requests_24h": api_requests, "all_healthy": len(active) == len(projects)}
