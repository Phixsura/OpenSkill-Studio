"""Per-request API metering (ADR-014 §3.3f).

Counts authenticated /api/v1 requests into Redis hourly buckets — zero DB
writes on the request path. A worker cron lands the previous hour's buckets
as api_request UsageEvents. Fail-open on any Redis error (user decision:
a Redis outage is an infra alert, not a platform-wide API kill).

Quota: max_api_requests_day checked from the day's hour buckets (MGET);
hard-over → 429 API_QUOTA_EXCEEDED. Order is INCR-then-check, so the 429
response itself is counted (simple + conservative).
"""

import re
from datetime import UTC, datetime

import jwt as _jwt
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.core.security import ALGORITHM

log = structlog.get_logger()

_ORG_PATH_RE = re.compile(r"^/api/v1/orgs/([0-9A-HJKMNP-TV-Z]{26})(/|$)")
_TENANT_PATH_RE = re.compile(r"^/api/v1/tenants/([0-9A-HJKMNP-TV-Z]{26})(/|$)")

# Never counted: platform ops, health, auth handshakes, docs, webhooks.
_EXCLUDED_PREFIXES = (
    "/api/v1/platform",
    "/api/v1/auth",
    "/api/v1/health",
    "/api/v1/docs",
    "/api/v1/redoc",
    "/api/v1/openapi.json",
    "/api/v1/billing/webhooks",
)

ORG_MAP_KEY = "cp:orgmap:{org_id}"
COUNTER_KEY = "cp:apireq:{tenant_id}:{bucket}"
QUOTA_CACHE_KEY = "cp:apiquota:{tenant_id}"


def _local_day_buckets(tz_name: str, now: datetime) -> list[str]:
    """UTC hour-bucket names covering the tenant-local calendar day of `now`.

    R53[2]: the quota window is the TENANT-local day (matches rating/budget
    period conventions). Counters stay keyed by UTC hour — this maps the
    local day [00:00, 24:00) onto the UTC hour buckets it spans. Pure logic,
    unit-testable. Bad tz falls back to UTC.
    """
    from datetime import timedelta
    from zoneinfo import ZoneInfo

    try:
        tz = ZoneInfo(tz_name)
    except Exception:  # noqa: BLE001
        tz = UTC
    local = now.astimezone(tz)
    day_start = local.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(UTC)
    # R113[L4]: a DST-transition day is 23 or 25 hours — a fixed 24-hour
    # window either misses the day's last hour (under-count → quota leak) or
    # double-counts into tomorrow. Compute the real day length.
    next_day_start = (
        (local + timedelta(days=1))
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .astimezone(UTC)
    )
    hours = max(int((next_day_start - day_start).total_seconds() // 3600), 1)
    return [(day_start + timedelta(hours=h)).strftime("%Y%m%d%H") for h in range(hours)]


def classify_path(path: str) -> str | None:
    """Return 'org:<id>' / 'tenant:<id>' / None (not counted). Pure logic —
    unit-tested without Redis."""
    if not path.startswith("/api/v1/"):
        return None
    for prefix in _EXCLUDED_PREFIXES:
        if path.startswith(prefix):
            return None
    m = _ORG_PATH_RE.match(path)
    if m:
        return f"org:{m.group(1)}"
    m = _TENANT_PATH_RE.match(path)
    if m:
        return f"tenant:{m.group(1)}"
    # Other authenticated API traffic (registry browsing, portfolio, …) is
    # not tenant-attributable → not counted (public surface stays free).
    return None


class ApiRequestMeteringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        target = classify_path(request.url.path)
        if target is None:
            return await call_next(request)
        auth = request.headers.get("authorization", "")
        # Match FastAPI's case-insensitive scheme parse so a lowercase `bearer`
        # (or extra whitespace) can't skip metering + daily-quota enforcement
        # while the route still authenticates the token.
        scheme, _, token = auth.partition(" ")
        if scheme.lower() != "bearer":
            return await call_next(request)
        try:
            _jwt.decode(token.strip(), settings.jwt_secret, algorithms=[ALGORITHM])
        except Exception:  # noqa: BLE001 — invalid token → route auth's problem, not counted
            return await call_next(request)

        try:
            tenant_id = await self._resolve_tenant(target)
            if tenant_id is None:
                return await call_next(request)
            over = await self._count_and_check(tenant_id)
            if over:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "API_QUOTA_EXCEEDED",
                            "message": "Daily API request quota exceeded",
                            "request_id": getattr(request.state, "request_id", None),
                        }
                    },
                )
        except Exception:  # noqa: BLE001 — fail-open: metering must never break the API
            log.debug("cp_api_metering_skipped", path=request.url.path)
        return await call_next(request)

    @staticmethod
    async def _resolve_tenant(target: str) -> str | None:
        from app.core.redis import redis_pool

        kind, ref_id = target.split(":", 1)
        if kind == "tenant":
            return ref_id
        r = redis_pool()
        cache_key = ORG_MAP_KEY.format(org_id=ref_id)
        cached = await r.get(cache_key)
        if cached:
            return cached.decode() if isinstance(cached, bytes) else cached
        # DB fallback — one indexed point lookup, cached 300s
        from sqlalchemy import select

        from app.core.database import AsyncSessionLocal
        from app.models.organization import Organization

        async with AsyncSessionLocal() as db:
            tenant_id = (
                await db.execute(select(Organization.tenant_id).where(Organization.id == ref_id))
            ).scalar_one_or_none()
        if tenant_id:
            await r.set(cache_key, tenant_id, ex=300)
        return tenant_id

    @staticmethod
    async def _count_and_check(tenant_id: str) -> bool:
        """INCR this hour's bucket, then compare the day total against the
        cached quota. Returns True when hard-over."""
        from app.core.redis import redis_pool

        r = redis_pool()
        now = datetime.now(UTC)
        bucket = now.strftime("%Y%m%d%H")
        key = COUNTER_KEY.format(tenant_id=tenant_id, bucket=bucket)
        async with r.pipeline(transaction=False) as pipe:
            pipe.incr(key)
            pipe.expire(key, 90_000)  # 25h — outlives the hourly flush
            await pipe.execute()

        quota_raw = await r.get(QUOTA_CACHE_KEY.format(tenant_id=tenant_id))
        if quota_raw is None:
            # Quota resolution requires the entitlement engine (DB). Cache it
            # for 5 minutes; "unlimited" cached as -1. R53[2]: the tenant's
            # timezone rides the same cache entry ("quota|tz") — the daily
            # window is the TENANT-local calendar day (period convention),
            # not the UTC day, which reset mid-business-day for most of the
            # world and mis-sized the quota around midnight.
            from app.controlplane.models.tenant import TenantAccount
            from app.controlplane.services.entitlements import get_effective
            from app.core.database import AsyncSessionLocal

            async with AsyncSessionLocal() as db:
                tenant = await db.get(TenantAccount, tenant_id)
                if tenant is None:
                    return False
                eff = await get_effective(db, tenant)
                limit = eff.get("max_api_requests_day")
                tz_name = tenant.timezone
            quota = -1 if limit is None else int(limit)
            # R92[m2]: honor the entitlement dirty tombstone — a metered
            # request racing a pre-commit mutation otherwise re-cached the
            # STALE quota for 300s (get_effective computes from the pre-write
            # snapshot while the tombstone lives; the ent-cache respects it,
            # this secondary cache didn't).
            if not await r.get(f"cp:entdirty:{tenant_id}"):
                await r.set(
                    QUOTA_CACHE_KEY.format(tenant_id=tenant_id), f"{quota}|{tz_name}", ex=300
                )
        else:
            raw = quota_raw.decode() if isinstance(quota_raw, bytes) else str(quota_raw)
            quota_s, _, tz_name = raw.partition("|")
            quota = int(quota_s)
            tz_name = tz_name or "UTC"
        if quota < 0:
            return False
        keys = [
            COUNTER_KEY.format(tenant_id=tenant_id, bucket=b)
            for b in _local_day_buckets(tz_name, now)
        ]
        values = await r.mget(keys)
        total = sum(int(v) for v in values if v)
        return total > quota
