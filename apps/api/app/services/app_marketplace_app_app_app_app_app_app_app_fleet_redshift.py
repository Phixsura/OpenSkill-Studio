"""Fleet Redshift — track data warehouse health."""
from __future__ import annotations
def fleet_redshift_status(clusters: list[dict]) -> dict:
    available = [c for c in clusters if c.get("status") == "available"]
    total_nodes = sum(c.get("nodes", 0) for c in clusters)
    storage_pct = round(sum(c.get("storage_pct", 0) for c in clusters) / max(len(clusters), 1), 1)
    return {"clusters": len(clusters), "available": len(available), "nodes": total_nodes,
            "storage_pct": storage_pct, "healthy": storage_pct < 80}
