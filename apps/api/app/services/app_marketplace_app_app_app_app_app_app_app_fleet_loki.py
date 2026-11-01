"""Fleet Loki — track log aggregation health."""
from __future__ import annotations
def fleet_loki_status(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    ingestion_rate = sum(i.get("ingestion_mb_per_sec", 0) for i in instances)
    query_avg_ms = round(sum(i.get("query_avg_ms", 0) for i in instances) / max(len(instances), 1), 1)
    return {"instances": len(instances), "healthy": len(healthy), "ingestion_mb_per_sec": round(ingestion_rate, 1),
            "query_avg_ms": query_avg_ms, "all_healthy": len(healthy) == len(instances)}
