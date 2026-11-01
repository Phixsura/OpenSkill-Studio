"""Extension Storage Bucket — object storage for extension files."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import time


@dataclass
class StorageObject:
    key: str
    extension_id: str
    size_bytes: int
    content_type: str
    etag: str
    uploaded_at: float = 0.0
    public: bool = False
    def __post_init__(self):
        if not self.uploaded_at: self.uploaded_at = time.time()


class ExtStorageBucketService:
    MAX_OBJECT_SIZE = 50 * 1024 * 1024  # 50MB

    def __init__(self):
        self._objects: dict[str, dict[str, StorageObject]] = {}  # ext_id -> {key -> obj}

    def put(self, extension_id: str, key: str, data: bytes,
            content_type: str = "application/octet-stream", public: bool = False) -> StorageObject:
        if len(data) > self.MAX_OBJECT_SIZE:
            raise ValueError(f"Object too large: {len(data)} > {self.MAX_OBJECT_SIZE}")
        if ".." in key or key.startswith("/"):
            raise ValueError("Invalid key")
        etag = hashlib.md5(data).hexdigest()
        obj = StorageObject(key=key, extension_id=extension_id,
                            size_bytes=len(data), content_type=content_type,
                            etag=etag, public=public)
        if extension_id not in self._objects:
            self._objects[extension_id] = {}
        self._objects[extension_id][key] = obj
        return obj

    def get(self, extension_id: str, key: str) -> StorageObject | None:
        return self._objects.get(extension_id, {}).get(key)

    def delete(self, extension_id: str, key: str) -> bool:
        bucket = self._objects.get(extension_id, {})
        return bucket.pop(key, None) is not None

    def list_objects(self, extension_id: str, prefix: str = "") -> list[StorageObject]:
        bucket = self._objects.get(extension_id, {})
        objs = list(bucket.values())
        if prefix:
            objs = [o for o in objs if o.key.startswith(prefix)]
        return sorted(objs, key=lambda o: o.key)

    def get_usage(self, extension_id: str) -> dict:
        bucket = self._objects.get(extension_id, {})
        total = sum(o.size_bytes for o in bucket.values())
        return {"object_count": len(bucket), "total_bytes": total}
