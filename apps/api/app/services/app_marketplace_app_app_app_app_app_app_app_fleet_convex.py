"""Fleet Convex — track reactive backend platform."""
from __future__ import annotations
def fleet_convex_status(projects: list[dict]) -> dict:
    deployed = [p for p in projects if p.get("deployed", True)]
    functions = sum(p.get("functions", 0) for p in projects)
    documents = sum(p.get("documents", 0) for p in projects)
    return {"projects": len(projects), "deployed": len(deployed), "functions": functions,
            "documents": documents, "all_deployed": len(deployed) == len(projects)}
