"""Redis sliding-window rate limiting."""

import time

import jwt as _jwt
import structlog
from fastapi import HTTPException, Request
from redis.asyncio import Redis

from app.config import settings
from app.core.redis import redis_pool

log = structlog.get_logger()


def client_identity(request: Request) -> str:
    """Rate-limit principal (R78b, issue-18 addendum).

    Priority: (1) the AUTHENTICATED user id when the request carries a valid
    access token — behind NAT/proxies many users share one IP, and one
    abuser's bucket must not starve everyone else's; (2) the real client IP
    recovered from X-Forwarded-For when settings.trusted_proxy_hops > 0
    (each trusted proxy appends its caller, so the client is the N-th entry
    from the right); (3) the direct peer IP. Forwarded headers are IGNORED at
    the default 0 hops — an untrusted client could otherwise spoof arbitrary
    identities and mint unlimited buckets."""
    auth = request.headers.get("authorization", "")
    if not isinstance(auth, str):  # defensive: mocked/exotic header objects
        auth = ""
    scheme, _, token = auth.partition(" ")
    if scheme.lower() == "bearer" and token.strip():
        try:
            from app.core.security import ALGORITHM

            payload = _jwt.decode(token.strip(), settings.jwt_secret, algorithms=[ALGORITHM])
            sub = payload.get("sub")
            if sub:
                return f"u:{sub}"
        except Exception:  # noqa: BLE001 — invalid token → fall through to IP
            pass
    hops = settings.trusted_proxy_hops
    if hops > 0:
        xff = request.headers.get("x-forwarded-for", "")
        if not isinstance(xff, str):
            xff = ""
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts:
            # Fewer entries than trusted hops = a trusted proxy connected
            # directly (header shorter than the chain) — leftmost is best.
            return "ip:" + (parts[-hops] if len(parts) >= hops else parts[0])
    return "ip:" + (request.client.host if request.client else "unknown")


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
    """FastAPI dependency for rate limiting by client IP, keyed on the ROUTE
    TEMPLATE (not the concrete URL).

    Keying on ``request.url.path`` (the concrete path) let every distinct value
    of a high-cardinality path parameter mint a fresh independent bucket, so an
    endpoint with a ``{project_id}``/``{pack_id}`` in its path had effectively
    no aggregate ceiling: the creator-shortlist (``/orgs/{org_id}/projects/
    {project_id}/creator-shortlist``), which runs a full-org creator scoring
    pass and persists a MatchRun + MatchResult rows PER CALL, could be hit
    limit×(number of accessible projects) per window from one client — compute +
    DB-write amplification (R75b). Using the route template collapses all
    path-parameter values into a single bucket, so the limit is real per
    (method, route, IP).
    """

    async def checker(request: Request):
        if settings.app_env == "test":
            return limit  # Skip rate limiting in tests

        identity = client_identity(request)
        # Route TEMPLATE, not the concrete URL — a path param must not shard the
        # bucket. Fall back to the concrete path only if the route is somehow
        # unresolved (defensive; every mounted route carries scope["route"]).
        route = request.scope.get("route")
        path_key = getattr(route, "path", None) or request.url.path
        key = f"{request.method}:{path_key}:{identity}"

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
