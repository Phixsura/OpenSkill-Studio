"""Fleet AI Data Pipeline — track data ingestion and transformation flows."""
from __future__ import annotations
def fleet_ai_data_pipeline(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    records_24h = sum(p.get("records_24h", 0) for p in pipelines)
    throughput_mbs = sum(p.get("throughput_mbs", 0) for p in pipelines)
    return {"pipelines": len(pipelines), "active": len(active), "records_24h": records_24h,
            "throughput_mbs": throughput_mbs, "flowing": len(active) == len(pipelines)}
