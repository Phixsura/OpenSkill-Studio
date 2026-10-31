"""Fleet OpenSearch — track open-source search analytics."""
from __future__ import annotations
def fleet_opensearch_status(clusters: list[dict]) -> dict:
    green = [c for c in clusters if c.get("status") == "green"]
    total_docs = sum(c.get("documents", 0) for c in clusters)
    shards = sum(c.get("shards", 0) for c in clusters)
    return {"clusters": len(clusters), "green": len(green), "documents": total_docs,
            "shards": shards, "all_green": len(green) == len(clusters)}
