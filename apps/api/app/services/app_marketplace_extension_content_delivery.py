"""Extension Content Delivery — CDN edge caching for extension assets."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time


@dataclass
class CachedAsset:
    path: str
    extension_id: str
    content_hash: str
    size_bytes: int
    content_type: str
    cache_control: str = "public, max-age=86400"
    edge_locations: list[str] = field(default_factory=list)
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtContentDeliveryService:
    EDGE_LOCATIONS = ["us-east", "us-west", "eu-west", "eu-central", "ap-southeast", "ap-northeast"]

    def __init__(self):
        self._assets: dict[str, CachedAsset] = {}  # path -> asset
        self._total_bandwidth = 0

    def publish(self, extension_id: str, path: str, content: bytes,
                content_type: str = "application/javascript") -> CachedAsset:
        content_hash = hashlib.sha256(content).hexdigest()[:16]
        asset = CachedAsset(
            path=path, extension_id=extension_id,
            content_hash=content_hash, size_bytes=len(content),
            content_type=content_type, edge_locations=list(self.EDGE_LOCATIONS))
        self._assets[path] = asset
        return asset

    def get(self, path: str) -> CachedAsset | None:
        asset = self._assets.get(path)
        if asset:
            self._total_bandwidth += asset.size_bytes
        return asset

    def invalidate(self, path: str) -> bool:
        return self._assets.pop(path, None) is not None

    def invalidate_extension(self, extension_id: str) -> int:
        paths = [p for p, a in self._assets.items() if a.extension_id == extension_id]
        for p in paths:
            del self._assets[p]
        return len(paths)

    def get_stats(self) -> dict:
        return {
            "total_assets": len(self._assets),
            "total_size_bytes": sum(a.size_bytes for a in self._assets.values()),
            "total_bandwidth": self._total_bandwidth,
            "edge_locations": len(self.EDGE_LOCATIONS),
        }
