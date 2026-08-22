from redis.asyncio import Redis, from_url

from app.config import settings

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
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    return _redis
