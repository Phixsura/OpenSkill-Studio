"""Fleet ElastiCache — track managed cache cluster health."""
from __future__ import annotations
def fleet_elasticache_status(clusters: list[dict]) -> dict:
    available = [c for c in clusters if c.get("status") == "available"]
    total_nodes = sum(c.get("nodes", 0) for c in clusters)
    memory_pct = round(sum(c.get("memory_pct", 0) for c in clusters) / max(len(clusters), 1), 1)
    return {"clusters": len(clusters), "available": len(available), "nodes": total_nodes,
            "memory_pct": memory_pct, "healthy": memory_pct < 80}
