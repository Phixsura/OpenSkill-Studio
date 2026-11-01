"""Per-app and per-installation rate limiting.

Tracks API usage per app/installation for observability and enforcement.
Uses in-memory counters (production: Redis).
"""

from collections import defaultdict
from datetime import UTC, datetime

import structlog

log = structlog.get_logger()

# In-memory counters: {app_id: {hour_key: count}}
_APP_COUNTERS: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
_INSTALL_COUNTERS: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

# Rate limits per tier
RATE_LIMITS = {
    "standard": 1000,  # requests per hour
    "elevated": 5000,
    "unlimited": 0,  # 0 = no limit
}


def _hour_key() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d-%H")


def record_request(app_id: str, installation_id: str | None = None) -> None:
    """Record an API request for rate tracking."""
    key = _hour_key()
    _APP_COUNTERS[app_id][key] += 1
    if installation_id:
        _INSTALL_COUNTERS[installation_id][key] += 1


def get_app_usage(app_id: str) -> dict:
    """Get current hour's usage for an app."""
    key = _hour_key()
    return {
        "app_id": app_id,
        "hour": key,
        "requests": _APP_COUNTERS.get(app_id, {}).get(key, 0),
    }


def get_installation_usage(installation_id: str) -> dict:
    """Get current hour's usage for an installation."""
    key = _hour_key()
    return {
        "installation_id": installation_id,
        "hour": key,
        "requests": _INSTALL_COUNTERS.get(installation_id, {}).get(key, 0),
    }


def check_rate_limit(app_id: str, tier: str = "standard") -> bool:
    """Check if an app has exceeded its rate limit.

    Returns True if the request should be allowed, False if rate limited.
    """
    limit = RATE_LIMITS.get(tier, RATE_LIMITS["standard"])
    if limit == 0:
        return True  # unlimited

    key = _hour_key()
    current = _APP_COUNTERS.get(app_id, {}).get(key, 0)
    return current < limit


def get_rate_limit_headers(app_id: str, tier: str = "standard") -> dict[str, str]:
    """Get X-RateLimit-* headers for API responses."""
    limit = RATE_LIMITS.get(tier, RATE_LIMITS["standard"])
    key = _hour_key()
    current = _APP_COUNTERS.get(app_id, {}).get(key, 0)

    if limit == 0:
        return {
            "X-RateLimit-Limit": "unlimited",
            "X-RateLimit-Remaining": "unlimited",
        }

    remaining = max(0, limit - current)
    # Calculate reset time (next hour)
    now = datetime.now(UTC)
    reset = now.replace(minute=0, second=0, microsecond=0)
    from datetime import timedelta

    reset += timedelta(hours=1)

    return {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(reset.timestamp())),
    }


def cleanup_old_counters() -> int:
    """Remove counters older than current hour. Returns count removed."""
    current = _hour_key()
    removed = 0
    for app_counters in _APP_COUNTERS.values():
        old_keys = [k for k in app_counters if k != current]
        for k in old_keys:
            del app_counters[k]
            removed += 1
    for inst_counters in _INSTALL_COUNTERS.values():
        old_keys = [k for k in inst_counters if k != current]
        for k in old_keys:
            del inst_counters[k]
            removed += 1
    return removed
