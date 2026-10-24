"""Fleet ElasticSearch — track search cluster health."""
from __future__ import annotations
def fleet_elastic_status(cluster: dict) -> dict:
    status = cluster.get("status", "green")
    nodes = cluster.get("nodes", 0)
    shards = cluster.get("active_shards", 0)
    unassigned = cluster.get("unassigned_shards", 0)
    return {"status": status, "nodes": nodes, "active_shards": shards,
            "unassigned_shards": unassigned, "healthy": status == "green"}
