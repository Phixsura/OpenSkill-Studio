"""Fleet Typesense — track typo-tolerant search engine."""
from __future__ import annotations
def fleet_typesense_status(nodes: list[dict]) -> dict:
    healthy = [n for n in nodes if n.get("healthy", True)]
    collections = sum(n.get("collections", 0) for n in nodes)
    documents = sum(n.get("documents", 0) for n in nodes)
    return {"nodes": len(nodes), "healthy": len(healthy), "collections": collections,
            "documents": documents, "all_healthy": len(healthy) == len(nodes)}
