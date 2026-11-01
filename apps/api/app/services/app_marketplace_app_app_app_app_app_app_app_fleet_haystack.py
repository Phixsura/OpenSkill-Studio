"""Fleet Haystack — track NLP pipeline framework."""
from __future__ import annotations
def fleet_haystack_status(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    nodes = sum(p.get("nodes", 0) for p in pipelines)
    queries_24h = sum(p.get("queries_24h", 0) for p in pipelines)
    return {"pipelines": len(pipelines), "active": len(active), "nodes": nodes,
            "queries_24h": queries_24h, "all_active": len(active) == len(pipelines)}
