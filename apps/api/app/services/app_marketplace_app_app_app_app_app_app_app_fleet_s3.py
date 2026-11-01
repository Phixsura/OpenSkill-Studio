"""Fleet S3 — track object storage health and usage."""
from __future__ import annotations
def fleet_s3_status(buckets: list[dict]) -> dict:
    total_objects = sum(b.get("objects", 0) for b in buckets)
    total_size_tb = sum(b.get("size_tb", 0) for b in buckets)
    versioned = [b for b in buckets if b.get("versioning", False)]
    encrypted = [b for b in buckets if b.get("encrypted", False)]
    return {"buckets": len(buckets), "objects": total_objects, "size_tb": round(total_size_tb, 1),
            "versioned": len(versioned), "encrypted": len(encrypted), "secure": len(encrypted) == len(buckets)}
