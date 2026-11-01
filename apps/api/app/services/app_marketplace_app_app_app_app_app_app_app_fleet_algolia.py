"""Fleet Algolia — track hosted search service."""
from __future__ import annotations
def fleet_algolia_status(indices: list[dict]) -> dict:
    total_records = sum(i.get("records", 0) for i in indices)
    operations_24h = sum(i.get("operations_24h", 0) for i in indices)
    avg_latency_ms = round(sum(i.get("avg_latency_ms", 0) for i in indices) / max(len(indices), 1), 1)
    return {"indices": len(indices), "records": total_records, "operations_24h": operations_24h,
            "avg_latency_ms": avg_latency_ms, "fast": avg_latency_ms < 20}
