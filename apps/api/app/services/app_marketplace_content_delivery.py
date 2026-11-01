"""Content Delivery — manage extension asset distribution via CDN.

Tracks extension assets (JS bundles, icons, screenshots), generates
CDN URLs, manages cache invalidation, and monitors delivery metrics.
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class CDNAsset:
    asset_id: str
    extension_id: str
    version: str
    path: str  # e.g. "dist/bundle.js"
    content_hash: str
    size_bytes: int
    content_type: str
    cdn_url: str = ""
    uploaded_at: str = ""
    cache_ttl: int = 86400  # 1 day default

    def __post_init__(self):
        if not self.uploaded_at:
            self.uploaded_at = datetime.now(timezone.utc).isoformat()
        if not self.cdn_url:
            self.cdn_url = f"https://cdn.openskill.dev/ext/{self.extension_id}/{self.version}/{self.path}?h={self.content_hash[:8]}"


class ContentDeliveryService:
    """Manages CDN asset distribution for extensions."""

    CDN_BASE = "https://cdn.openskill.dev/ext"

    def __init__(self):
        self._assets: dict[str, CDNAsset] = {}
        self._invalidations: list[dict] = []

    def upload_asset(self, extension_id: str, version: str, path: str,
                     content: bytes, content_type: str = "application/octet-stream") -> CDNAsset:
        """Upload an asset to CDN."""
        content_hash = hashlib.sha256(content).hexdigest()
        asset_id = f"{extension_id}/{version}/{path}"
        asset = CDNAsset(
            asset_id=asset_id, extension_id=extension_id,
            version=version, path=path,
            content_hash=content_hash, size_bytes=len(content),
            content_type=content_type,
        )
        self._assets[asset_id] = asset
        return asset

    def get_asset(self, extension_id: str, version: str, path: str) -> CDNAsset | None:
        return self._assets.get(f"{extension_id}/{version}/{path}")

    def get_cdn_url(self, extension_id: str, version: str, path: str) -> str | None:
        asset = self.get_asset(extension_id, version, path)
        return asset.cdn_url if asset else None

    def list_assets(self, extension_id: str, version: str = "") -> list[CDNAsset]:
        assets = [a for a in self._assets.values() if a.extension_id == extension_id]
        if version:
            assets = [a for a in assets if a.version == version]
        return sorted(assets, key=lambda a: a.path)

    def invalidate_cache(self, extension_id: str, version: str, paths: list[str] | None = None) -> dict:
        """Invalidate CDN cache for specific paths or entire version."""
        target = paths or ["*"]
        record = {
            "extension_id": extension_id, "version": version,
            "paths": target,
            "invalidated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._invalidations.append(record)
        return record

    def get_total_size(self, extension_id: str, version: str = "") -> int:
        return sum(a.size_bytes for a in self.list_assets(extension_id, version))

    def delete_version_assets(self, extension_id: str, version: str) -> int:
        to_delete = [k for k, a in self._assets.items()
                     if a.extension_id == extension_id and a.version == version]
        for k in to_delete:
            del self._assets[k]
        return len(to_delete)
