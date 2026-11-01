"""Fleet TiDB — track distributed SQL database."""
from __future__ import annotations
def fleet_tidb_status(clusters: list[dict]) -> dict:
    healthy = [c for c in clusters if c.get("healthy", True)]
    tikv_stores = sum(c.get("tikv_stores", 0) for c in clusters)
    qps = sum(c.get("qps", 0) for c in clusters)
    return {"clusters": len(clusters), "healthy": len(healthy), "tikv_stores": tikv_stores,
            "qps": qps, "all_healthy": len(healthy) == len(clusters)}
