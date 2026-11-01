"""Fleet Memcached — track distributed cache health."""
from __future__ import annotations
def fleet_memcached_status(nodes: list[dict]) -> dict:
    alive = [n for n in nodes if n.get("alive", True)]
    total_items = sum(n.get("items", 0) for n in nodes)
    hit_rate = round(sum(n.get("hit_rate_pct", 0) for n in nodes) / max(len(nodes), 1), 1)
    return {"nodes": len(nodes), "alive": len(alive), "items": total_items,
            "hit_rate_pct": hit_rate, "effective": hit_rate >= 80}
