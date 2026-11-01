"""Fleet Weaviate — track vector database health."""
from __future__ import annotations
def fleet_weaviate_status(nodes: list[dict]) -> dict:
    healthy = [n for n in nodes if n.get("healthy", True)]
    total_objects = sum(n.get("objects", 0) for n in nodes)
    total_vectors = sum(n.get("vectors", 0) for n in nodes)
    return {"nodes": len(nodes), "healthy": len(healthy), "objects": total_objects,
            "vectors": total_vectors, "all_healthy": len(healthy) == len(nodes)}
