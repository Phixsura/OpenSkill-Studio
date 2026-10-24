"""Fleet Milvus — track Milvus vector DB cluster health."""
from __future__ import annotations
def fleet_milvus_status(nodes: list[dict]) -> dict:
    healthy = [n for n in nodes if n.get("healthy", True)]
    total_entities = sum(n.get("entities", 0) for n in nodes)
    search_qps = sum(n.get("search_qps", 0) for n in nodes)
    return {"nodes": len(nodes), "healthy": len(healthy), "entities": total_entities,
            "search_qps": search_qps, "all_healthy": len(healthy) == len(nodes)}
