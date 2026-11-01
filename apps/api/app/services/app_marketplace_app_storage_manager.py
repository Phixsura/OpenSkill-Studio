"""Storage manager — manage app file storage and object buckets."""

import secrets


def create_bucket(*, app_id: str, name: str, region: str = "us-east-1",
                    access: str = "private") -> dict:
    valid_access = {"private", "public-read", "authenticated"}
    if access not in valid_access:
        return {"error": f"Invalid access. Valid: {', '.join(sorted(valid_access))}"}
    bucket_id = f"bkt_{secrets.token_urlsafe(8)}"
    return {
        "bucket_id": bucket_id,
        "app_id": app_id,
        "name": name,
        "region": region,
        "access": access,
        "url": f"https://storage.openskill.dev/{bucket_id}",
        "status": "active",
        "size_bytes": 0,
        "object_count": 0,
    }


def get_storage_usage(*, buckets: list[dict]) -> dict:
    total_bytes = sum(b.get("size_bytes", 0) for b in buckets)
    total_objects = sum(b.get("object_count", 0) for b in buckets)
    total_gb = round(total_bytes / (1024 ** 3), 2)
    return {
        "total_buckets": len(buckets),
        "total_size_gb": total_gb,
        "total_objects": total_objects,
        "buckets": [{"name": b["name"], "size_gb": round(b.get("size_bytes", 0) / (1024**3), 3),
                      "objects": b.get("object_count", 0)} for b in buckets],
    }
