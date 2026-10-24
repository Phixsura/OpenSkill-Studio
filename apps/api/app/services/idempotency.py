"""Idempotency key service for API requests.

Ensures POST/PATCH requests with the same Idempotency-Key header
return the same response without re-executing the operation.
Uses a simple in-memory cache (production: Redis).
"""

import hashlib
from datetime import UTC, datetime
from typing import Any

import structlog

log = structlog.get_logger()

# In-memory store (production: Redis with TTL)
_IDEMPOTENCY_STORE: dict[str, dict[str, Any]] = {}
MAX_ENTRIES = 10_000
TTL_SECONDS = 86_400  # 24 hours


def _cleanup() -> None:
    """Evict expired entries."""
    now = datetime.now(UTC).timestamp()
    expired = [
        k for k, v in _IDEMPOTENCY_STORE.items() if now - v["created_at"] > TTL_SECONDS
    ]
    for k in expired:
        del _IDEMPOTENCY_STORE[k]


def get_cached_response(key: str) -> dict | None:
    """Look up a cached response by idempotency key.

    Returns the stored response dict, or None if not found/expired.
    """
    entry = _IDEMPOTENCY_STORE.get(key)
    if entry is None:
        return None

    # Check TTL
    age = datetime.now(UTC).timestamp() - entry["created_at"]
    if age > TTL_SECONDS:
        del _IDEMPOTENCY_STORE[key]
        return None

    log.debug("idempotency_cache_hit", key=key[:16])
    return entry["response"]


def store_response(key: str, response: dict, status_code: int = 200) -> None:
    """Cache a response for an idempotency key."""
    # Cleanup if too many entries
    if len(_IDEMPOTENCY_STORE) >= MAX_ENTRIES:
        _cleanup()

    _IDEMPOTENCY_STORE[key] = {
        "response": response,
        "status_code": status_code,
        "created_at": datetime.now(UTC).timestamp(),
    }
    log.debug("idempotency_cache_stored", key=key[:16])


def make_key(client_key: str, method: str, path: str) -> str:
    """Create a composite idempotency key from client key + request identity."""
    return hashlib.sha256(f"{client_key}:{method}:{path}".encode()).hexdigest()
