"""Fleet Vercel — track edge deployment health."""
from __future__ import annotations
def fleet_vercel_status(projects: list[dict]) -> dict:
    deployed = [p for p in projects if p.get("status") == "READY"]
    total_requests = sum(p.get("requests_24h", 0) for p in projects)
    edge_functions = sum(p.get("edge_functions", 0) for p in projects)
    return {"projects": len(projects), "deployed": len(deployed), "requests_24h": total_requests,
            "edge_functions": edge_functions, "all_deployed": len(deployed) == len(projects)}
