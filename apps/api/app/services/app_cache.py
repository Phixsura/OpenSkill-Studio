"""App cache — simple in-memory cache with TTL for app lookups."""

import time
from collections import OrderedDict

_cache: OrderedDict[str, tuple[float, object]] = OrderedDict()
DEFAULT_TTL = 300  # 5 minutes
MAX_ENTRIES = 1000


def cache_get(key: str) -> object | None:
    """Get a value from cache if not expired."""
    entry = _cache.get(key)
    if entry is None:
        return None
    expiry, value = entry
    if time.monotonic() > expiry:
        _cache.pop(key, None)
        return None
    _cache.move_to_end(key)
    return value


def cache_set(key: str, value: object, ttl: int = DEFAULT_TTL) -> None:
    """Set a value in cache with TTL."""
    _cache[key] = (time.monotonic() + ttl, value)
    _cache.move_to_end(key)
    while len(_cache) > MAX_ENTRIES:
        _cache.popitem(last=False)


def cache_delete(key: str) -> bool:
    """Delete a cache entry. Returns True if existed."""
    return _cache.pop(key, None) is not None


def cache_clear() -> int:
    """Clear all cache entries."""
    count = len(_cache)
    _cache.clear()
    return count


def cache_size() -> int:
    return len(_cache)
