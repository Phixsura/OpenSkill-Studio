"""Redis sliding-window rate limiting."""

import time

import structlog
from fastapi import HTTPException, Request
from redis.asyncio import Redis

from app.config import settings
from app.core.redis import redis_pool

log = structlog.get_logger()


async def check_rate_limit(key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
    """
    Sliding window rate limit via Redis sorted set.
    Returns (is_allowed, remaining_requests).

    Two-phase approach: check count first, then conditionally add.
    Denied requests do NOT increment the counter.
    """
    try:
        r: Redis = redis_pool()
        now = time.time()
        window_start = now - window_seconds
        pipe_key = f"ratelimit:{key}"
        # Use a unique member to prevent collisions across concurrent requests
        member = f"{now}:{id(key)}:{time.monotonic_ns()}"

        # Phase 1: clean expired + count current
        async with r.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(pipe_key, 0, window_start)
            pipe.zcard(pipe_key)
            results = await pipe.execute()

        current_count = results[1]
        allowed = current_count < limit

        # Phase 2: only add if allowed
        if allowed:
            async with r.pipeline(transaction=True) as pipe:
                pipe.zadd(pipe_key, {member: now})
                pipe.expire(pipe_key, window_seconds)
                await pipe.execute()

        remaining = max(0, limit - current_count - (1 if allowed else 0))
        return allowed, remaining
    except Exception:
        if settings.app_env in ("development", "test"):
            # Fail-open in dev/test — allow request when Redis is unavailable
            log.debug("rate_limit_redis_unavailable", key=key)
            return True, limit
        # Fail-closed in production — deny request when Redis is unavailable
        log.warning("rate_limit_redis_unavailable_production", key=key)
        return False, 0


def rate_limit(limit: int, window: int):
    """FastAPI dependency for rate limiting by client IP."""

    async def checker(request: Request):
        if settings.app_env == "test":
            return limit  # Skip rate limiting in tests

        client_ip = request.client.host if request.client else "unknown"
        key = f"{request.method}:{request.url.path}:{client_ip}"

        allowed, remaining = await check_rate_limit(key, limit, window)

        # Set rate limit headers for transparency (RFC 6585 / draft-ietf-httpapi-ratelimit-headers)
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining if allowed else 0),
            "X-RateLimit-Reset": str(window),
        }

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={
                    "Retry-After": str(window),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(window),
                },
            )

        return remaining

    return checker
