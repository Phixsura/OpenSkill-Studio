"""Fleet Vectorize — track edge vector database."""
from __future__ import annotations
def fleet_vectorize_status(indexes: list[dict]) -> dict:
    active = [i for i in indexes if i.get("active", True)]
    total_vectors = sum(i.get("vectors", 0) for i in indexes)
    queries_24h = sum(i.get("queries_24h", 0) for i in indexes)
    return {"indexes": len(indexes), "active": len(active), "vectors": total_vectors,
            "queries_24h": queries_24h, "all_active": len(active) == len(indexes)}
