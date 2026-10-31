"""Storage bucket manager — manage object storage buckets."""
from __future__ import annotations

_buckets: dict[str, dict] = {}


def create_bucket(name: str, region: str = "us-east-1", public: bool = False) -> dict:
    if name in _buckets:
        return {"created": False, "error": "already_exists"}
    if not name.replace("-", "").replace(".", "").isalnum():
        return {"created": False, "error": "invalid_name"}
    _buckets[name] = {"name": name, "region": region, "public": public,
                       "objects": 0, "size_mb": 0.0}
    return {"created": True, "name": name, "region": region}


def upload_object(bucket: str, key: str, size_mb: float) -> dict:
    b = _buckets.get(bucket)
    if not b:
        return {"uploaded": False, "error": "bucket_not_found"}
    b["objects"] += 1
    b["size_mb"] = round(b["size_mb"] + size_mb, 2)
    return {"uploaded": True, "bucket": bucket, "key": key, "size_mb": size_mb}


def bucket_stats() -> dict:
    total_objects = sum(b["objects"] for b in _buckets.values())
    total_size = round(sum(b["size_mb"] for b in _buckets.values()), 2)
    return {"bucket_count": len(_buckets), "total_objects": total_objects,
            "total_size_mb": total_size}


def clear_buckets() -> None:
    _buckets.clear()
