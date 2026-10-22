"""Content delivery — CDN and asset management for app static files."""

import hashlib


def generate_asset_url(*, app_slug: str, version: str, path: str,
                         cdn_base: str = "https://cdn.openskill.dev") -> str:
    return f"{cdn_base}/apps/{app_slug}/{version}/{path}"


def compute_content_hash(*, content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()[:16]


def build_asset_manifest(*, assets: list[dict], version: str) -> dict:
    manifest = {}
    for a in assets:
        key = a.get("path", "")
        manifest[key] = {"hash": a.get("hash", ""), "size": a.get("size", 0),
                          "content_type": a.get("content_type", "application/octet-stream")}
    return {"version": version, "assets": manifest, "total_size": sum(a.get("size", 0) for a in assets)}


def invalidate_cache(*, paths: list[str], app_slug: str) -> dict:
    return {"app_slug": app_slug, "invalidated_paths": paths, "count": len(paths), "status": "completed"}
