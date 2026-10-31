"""Fleet Redis — track Redis cluster health."""
from __future__ import annotations
def fleet_redis_status(nodes: list[dict]) -> dict:
    masters = [n for n in nodes if n.get("role") == "master"]
    replicas = [n for n in nodes if n.get("role") == "replica"]
    total_keys = sum(n.get("keys", 0) for n in nodes)
    memory_pct = round(sum(n.get("memory_pct", 0) for n in nodes) / max(len(nodes), 1), 1)
    return {"nodes": len(nodes), "masters": len(masters), "replicas": len(replicas),
            "total_keys": total_keys, "memory_pct": memory_pct, "healthy": memory_pct < 80}
