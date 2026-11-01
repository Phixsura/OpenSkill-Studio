"""Fleet Solr — track search engine cluster health."""
from __future__ import annotations
def fleet_solr_status(collections: list[dict]) -> dict:
    active = [c for c in collections if c.get("state") == "active"]
    total_docs = sum(c.get("documents", 0) for c in collections)
    qps = sum(c.get("qps", 0) for c in collections)
    return {"collections": len(collections), "active": len(active), "documents": total_docs,
            "qps": qps, "all_active": len(active) == len(collections)}
