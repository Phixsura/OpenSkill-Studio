import structlog
from redis.asyncio import Redis, from_url

from app.config import settings

log = structlog.get_logger()

_redis: Redis | None = None


def redis_pool() -> Redis:
    """Return the shared async Redis connection."""
    global _redis  # noqa: PLW0603
    if _redis is None:
        _redis = from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=50,
            health_check_interval=30,
            # R196 (chaos probe: docker-paused Redis): 5s+5s socket timeouts
            # meant every cache-touching request blocked 10s (cache_get +
            # cache_set) during a Redis outage — fail-OPEN semantics held
            # (zero 500s) but the platform soft-died at 10s/page. Same-host
            # Redis p99 is single-digit ms; sub-second timeouts turn an
            # outage into ≤2s of degradation per cold request.
            socket_connect_timeout=0.5,
            socket_timeout=1.0,
        )
    return _redis


async def close_redis() -> None:
    """Close the Redis connection and invalidate the singleton.

    Call from lifespan shutdown so subsequent calls to redis_pool() don't
    silently operate on a closed connection.
    """
    global _redis  # noqa: PLW0603
    if _redis is not None:
        try:
            await _redis.aclose()
        except Exception:
            log.warning("redis_close_error")
        _redis = None
