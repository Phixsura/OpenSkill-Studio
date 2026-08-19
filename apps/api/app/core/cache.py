"""Redis caching helpers — fail-open when Redis is unavailable."""

import json

import structlog

from app.core.redis import redis_pool

log = structlog.get_logger()


async def cache_get(key: str) -> dict | None:
    """Get cached value. Returns None if Redis is unavailable or key missing."""
    try:
        r = redis_pool()
        data = await r.get(key)
        return json.loads(data) if data else None
    except Exception:
        log.debug("cache_get_unavailable", key=key)
        return None


async def cache_set(key: str, value: dict, ttl: int = 300) -> None:
    """Set cached value with TTL in seconds. No-op if Redis is unavailable."""
    try:
        r = redis_pool()
        await r.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception:
        log.debug("cache_set_unavailable", key=key)


async def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys matching pattern. No-op if Redis is unavailable."""
    try:
        r = redis_pool()
        keys: list = []
        async for key in r.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await r.delete(*keys)
    except Exception:
        log.debug("cache_delete_unavailable", pattern=pattern)
