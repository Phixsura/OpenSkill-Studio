"""Build cache manager — manage and optimize build caches."""
from __future__ import annotations
import hashlib
import time

_cache: dict[str, dict] = {}


def cache_build(build_key: str, layers: list[str], size_mb: float) -> dict:
    cache_hash = hashlib.sha256(":".join(layers).encode()).hexdigest()[:12]
    _cache[build_key] = {"key": build_key, "hash": cache_hash, "layers": len(layers),
                          "size_mb": round(size_mb, 1), "hits": 0,
                          "cached_at": time.time()}
    return {"cached": True, "key": build_key, "hash": cache_hash}


def lookup_cache(build_key: str) -> dict:
    entry = _cache.get(build_key)
    if not entry:
        return {"hit": False}
    entry["hits"] += 1
    return {"hit": True, **entry}


def cache_efficiency() -> dict:
    total_hits = sum(e["hits"] for e in _cache.values())
    total_size = round(sum(e["size_mb"] for e in _cache.values()), 1)
    return {"total_entries": len(_cache), "total_hits": total_hits,
            "total_size_mb": total_size,
            "avg_hits": round(total_hits / max(len(_cache), 1), 1)}


def clear_build_cache() -> None:
    _cache.clear()
