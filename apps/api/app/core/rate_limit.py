"""Redis sliding-window rate limiting."""

import time

import structlog
from fastapi import HTTPException, Request
from redis.asyncio import Redis

from app.core.redis import redis_pool

log = structlog.get_logger()


async def check_rate_limit(
    key: str, limit: int, window_seconds: int
) -> tuple[bool, int]:
    """
    Sliding window rate limit via Redis sorted set.
    Returns (is_allowed, remaining_requests).
    Falls back to allowing the request if Redis is unavailable.
    """
    try:
        r: Redis = redis_pool()
        now = time.time()
        window_start = now - window_seconds
        pipe_key = f"ratelimit:{key}"

        async with r.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(pipe_key, 0, window_start)
            pipe.zcard(pipe_key)
            pipe.zadd(pipe_key, {str(now): now})
            pipe.expire(pipe_key, window_seconds)
            results = await pipe.execute()

        current_count = results[1]
        allowed = current_count < limit
        remaining = max(0, limit - current_count - 1)

        return allowed, remaining
    except Exception:
        # Redis unavailable — allow request (fail-open for dev/test)
        log.debug("rate_limit_redis_unavailable", key=key)
        return True, limit


def rate_limit(limit: int, window: int):
    """FastAPI dependency for rate limiting by client IP."""

    async def checker(request: Request):
        import os

        if os.environ.get("APP_ENV") == "test":
            return limit  # Skip rate limiting in tests

        client_ip = request.client.host if request.client else "unknown"
        key = f"{request.url.path}:{client_ip}"

        allowed, remaining = await check_rate_limit(key, limit, window)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={"Retry-After": str(window)},
            )

        return remaining

    return checker
