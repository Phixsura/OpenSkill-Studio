"""Fleet LlamaIndex — track RAG application framework."""
from __future__ import annotations
def fleet_llamaindex_status(apps: list[dict]) -> dict:
    active = [a for a in apps if a.get("active", True)]
    indexes = sum(a.get("indexes", 0) for a in apps)
    queries_24h = sum(a.get("queries_24h", 0) for a in apps)
    return {"apps": len(apps), "active": len(active), "indexes": indexes,
            "queries_24h": queries_24h, "all_active": len(active) == len(apps)}
