"""Cache manager — in-memory TTL cache with stats."""
from __future__ import annotations
import time

_cache: dict[str, dict] = {}


def cache_set(key: str, value: object, ttl_sec: int = 300) -> dict:
    _cache[key] = {"value": value, "expires": time.time() + ttl_sec, "hits": 0}
    return {"key": key, "ttl_sec": ttl_sec, "stored": True}


def cache_get(key: str) -> dict:
    entry = _cache.get(key)
    if not entry:
        return {"key": key, "hit": False, "value": None}
    if time.time() > entry["expires"]:
        del _cache[key]
        return {"key": key, "hit": False, "value": None, "expired": True}
    entry["hits"] += 1
    return {"key": key, "hit": True, "value": entry["value"], "hits": entry["hits"]}


def cache_stats() -> dict:
    now = time.time()
    total = len(_cache)
    expired = sum(1 for e in _cache.values() if now > e["expires"])
    total_hits = sum(e["hits"] for e in _cache.values())
    return {"total_keys": total, "expired": expired, "active": total - expired,
            "total_hits": total_hits}


def cache_clear() -> dict:
    count = len(_cache)
    _cache.clear()
    return {"cleared": count}
