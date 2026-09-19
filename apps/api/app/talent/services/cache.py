"""Redis cache for talent layer — scoring profiles and matching results.

All functions degrade gracefully when Redis is unavailable (return None /
silently skip writes). This ensures the talent layer never crashes due to
cache infrastructure issues.
"""

from __future__ import annotations

import json
import logging
from typing import Any

log = logging.getLogger(__name__)


def _redis():
    """Lazy import to avoid circular dependencies at module load time."""
    from app.core.redis import redis_pool

    return redis_pool()


async def get_cached(key: str) -> dict | list | None:
    """Read a JSON-serialized value from Redis. Returns None on miss or error."""
    try:
        r = _redis()
        data = await r.get(key)
        if data is None:
            return None
        return json.loads(data)
    except Exception:
        log.debug("talent_cache_get_miss", extra={"key": key})
        return None


async def set_cached(key: str, value: Any, ttl: int = 300) -> None:
    """Write a JSON-serializable value to Redis with a TTL (seconds)."""
    try:
        r = _redis()
        await r.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception:
        log.debug("talent_cache_set_failed", extra={"key": key})


async def invalidate(pattern: str) -> None:
    """Delete all keys matching a glob pattern (e.g. 'talent:profile:USER*')."""
    try:
        r = _redis()
        cursor = 0
        while True:
            cursor, keys = await r.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await r.delete(*keys)
            if cursor == 0:
                break
    except Exception:
        log.debug("talent_cache_invalidate_failed", extra={"pattern": pattern})


def profile_cache_key(user_id: str) -> str:
    """Cache key for a user's full capability profile."""
    return f"talent:profile:{user_id}"


def match_cache_key(opportunity_id: str, limit: int = 20) -> str:
    """Cache key for match-candidates results."""
    return f"talent:match:{opportunity_id}:{limit}"


def user_match_cache_key(user_id: str, limit: int = 20) -> str:
    """Cache key for match-opportunities-for-user results."""
    return f"talent:match_user:{user_id}:{limit}"
