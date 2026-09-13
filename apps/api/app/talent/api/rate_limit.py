"""In-memory sliding-window rate limiter for talent API endpoints.

Adds standard headers to every response:
  X-RateLimit-Limit     — requests allowed per window
  X-RateLimit-Remaining — requests left in current window
  X-RateLimit-Reset     — Unix timestamp when the window resets

Returns 429 with Retry-After header when the limit is exceeded.

This is an in-memory implementation suitable for single-process deployments.
For multi-process or distributed setups, swap this for a Redis-backed limiter.
"""

from __future__ import annotations

from collections import defaultdict
from time import time

from fastapi import Depends, HTTPException, Request, Response

from app.api.deps import get_current_user
from app.models.user import User

# Configurable limits
WINDOW_SECONDS = 60
MAX_REQUESTS = 100

# In-memory store: key → list of request timestamps within window
_counters: dict[str, list[float]] = defaultdict(list)

# GC threshold: clean up stale keys every N requests
_GC_INTERVAL = 200
_request_count = 0


def _gc_stale_keys(now: float) -> None:
    """Remove keys with no recent timestamps to prevent memory leak."""
    stale = [
        key
        for key, timestamps in _counters.items()
        if not timestamps or timestamps[-1] < now - WINDOW_SECONDS
    ]
    for key in stale:
        del _counters[key]


async def rate_limit_talent(
    request: Request,
    response: Response,
    user: User = Depends(get_current_user),
) -> None:
    """FastAPI dependency that enforces per-user rate limiting.

    Add to a router via dependencies=[Depends(rate_limit_talent)].
    """
    global _request_count

    key = user.id
    now = time()

    # Periodic GC
    _request_count += 1
    if _request_count % _GC_INTERVAL == 0:
        _gc_stale_keys(now)

    # Trim expired timestamps
    cutoff = now - WINDOW_SECONDS
    timestamps = _counters[key]
    _counters[key] = [t for t in timestamps if t > cutoff]

    remaining = MAX_REQUESTS - len(_counters[key])
    reset_at = int(now) + WINDOW_SECONDS

    response.headers["X-RateLimit-Limit"] = str(MAX_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
    response.headers["X-RateLimit-Reset"] = str(reset_at)

    if remaining <= 0:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
            headers={
                "Retry-After": str(WINDOW_SECONDS),
                "X-RateLimit-Limit": str(MAX_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_at),
            },
        )

    _counters[key].append(now)


def reset_rate_limiter() -> None:
    """Reset all counters — useful for tests."""
    global _request_count
    _counters.clear()
    _request_count = 0
