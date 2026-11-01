"""Fleet R2 — track zero-egress object storage."""
from __future__ import annotations
def fleet_r2_status(buckets: list[dict]) -> dict:
    total_objects = sum(b.get("objects", 0) for b in buckets)
    storage_gb = sum(b.get("storage_gb", 0) for b in buckets)
    requests_24h = sum(b.get("requests_24h", 0) for b in buckets)
    return {"buckets": len(buckets), "objects": total_objects, "storage_gb": round(storage_gb, 1),
            "requests_24h": requests_24h, "in_use": total_objects > 0}
