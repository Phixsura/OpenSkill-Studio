"""Fleet Object Storage v9 — track S3-compatible bucket health."""
from __future__ import annotations
def fleet_object_storage_v9(buckets: list[dict]) -> dict:
    objects = sum(b.get("objects", 0) for b in buckets)
    size_tb = sum(b.get("size_tb", 0) for b in buckets)
    versioned = [b for b in buckets if b.get("versioning")]
    return {"buckets": len(buckets), "total_objects": objects, "size_tb": round(size_tb, 1),
            "versioned": len(versioned), "healthy": len(versioned) == len(buckets)}
