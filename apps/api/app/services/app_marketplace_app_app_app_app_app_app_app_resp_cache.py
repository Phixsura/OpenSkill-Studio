"""API response cache — cache and serve API responses."""
from __future__ import annotations
import hashlib
import time

_cache: dict[str, dict] = {}


def cache_key(method: str, path: str, params: str = "") -> str:
    return hashlib.sha256(f"{method}:{path}:{params}".encode()).hexdigest()[:16]


def get_cached(key: str) -> dict:
    entry = _cache.get(key)
    if not entry:
        return {"hit": False}
    if time.time() > entry["expires_at"]:
        del _cache[key]
        return {"hit": False, "expired": True}
    entry["hits"] += 1
    return {"hit": True, "data": entry["data"], "age_sec": round(time.time() - entry["cached_at"]),
            "hits": entry["hits"]}


def set_cached(key: str, data: dict, ttl_sec: int = 60) -> dict:
    now = time.time()
    _cache[key] = {"data": data, "cached_at": now, "expires_at": now + ttl_sec,
                    "hits": 0, "ttl_sec": ttl_sec}
    return {"cached": True, "key": key, "ttl_sec": ttl_sec}


def cache_metrics() -> dict:
    now = time.time()
    active = sum(1 for v in _cache.values() if now < v["expires_at"])
    total_hits = sum(v["hits"] for v in _cache.values())
    return {"total_keys": len(_cache), "active": active, "total_hits": total_hits}


def clear_cache() -> None:
    _cache.clear()
