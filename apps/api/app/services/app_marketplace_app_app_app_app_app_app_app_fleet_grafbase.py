"""Fleet Grafbase — track edge-native GraphQL backend."""
from __future__ import annotations
def fleet_grafbase_status(projects: list[dict]) -> dict:
    deployed = [p for p in projects if p.get("deployed", True)]
    resolvers = sum(p.get("resolvers", 0) for p in projects)
    requests_24h = sum(p.get("requests_24h", 0) for p in projects)
    return {"projects": len(projects), "deployed": len(deployed), "resolvers": resolvers,
            "requests_24h": requests_24h, "all_deployed": len(deployed) == len(projects)}
