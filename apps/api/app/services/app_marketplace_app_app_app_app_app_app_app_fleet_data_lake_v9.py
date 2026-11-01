"""Fleet Data Lake v9 — track data lake storage and query performance."""
from __future__ import annotations
def fleet_data_lake_v9(partitions: list[dict]) -> dict:
    size_tb = sum(p.get("size_tb", 0) for p in partitions)
    queries = sum(p.get("queries_per_hour", 0) for p in partitions)
    stale = [p for p in partitions if p.get("stale")]
    return {"partitions": len(partitions), "size_tb": round(size_tb, 1), "queries_per_hour": queries,
            "stale_partitions": len(stale), "healthy": len(stale) == 0}
