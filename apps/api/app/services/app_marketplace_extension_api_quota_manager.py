"""API Quota Manager — tiered quota enforcement with burst allowance and overage tracking.

Manages per-extension API quotas with configurable tiers (free/starter/pro/enterprise),
sliding window rate limiting, burst capacity, and overage notifications.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class QuotaTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_LIMITS: dict[QuotaTier, dict] = {
    QuotaTier.FREE: {"requests_per_hour": 100, "requests_per_day": 1000, "burst": 20},
    QuotaTier.STARTER: {"requests_per_hour": 1000, "requests_per_day": 10000, "burst": 100},
    QuotaTier.PRO: {"requests_per_hour": 10000, "requests_per_day": 100000, "burst": 500},
    QuotaTier.ENTERPRISE: {"requests_per_hour": 100000, "requests_per_day": 1000000, "burst": 5000},
}


@dataclass
class QuotaUsage:
    extension_id: str
    tier: QuotaTier
    hourly_used: int = 0
    daily_used: int = 0
    burst_used: int = 0
    total_requests: int = 0
    overage_count: int = 0
    last_reset_hour: str = ""
    last_reset_day: str = ""


@dataclass
class QuotaCheckResult:
    allowed: bool
    remaining_hourly: int
    remaining_daily: int
    burst_available: int
    used_burst: bool = False
    reason: str = ""


class ApiQuotaManagerService:
    """Enforces tiered API quotas with burst allowance."""

    def __init__(self):
        self._quotas: dict[str, QuotaUsage] = {}
        self._overrides: dict[str, dict] = {}

    def register(self, extension_id: str, tier: QuotaTier) -> QuotaUsage:
        now = datetime.now(timezone.utc).isoformat()
        usage = QuotaUsage(
            extension_id=extension_id, tier=tier,
            last_reset_hour=now, last_reset_day=now,
        )
        self._quotas[extension_id] = usage
        return usage

    def set_override(self, extension_id: str, requests_per_hour: int | None = None,
                     requests_per_day: int | None = None) -> None:
        override = {}
        if requests_per_hour is not None:
            override["requests_per_hour"] = requests_per_hour
        if requests_per_day is not None:
            override["requests_per_day"] = requests_per_day
        self._overrides[extension_id] = override

    def _get_limits(self, extension_id: str) -> dict:
        usage = self._quotas[extension_id]
        base = dict(TIER_LIMITS[usage.tier])
        override = self._overrides.get(extension_id, {})
        base.update(override)
        return base

    def check_and_consume(self, extension_id: str, count: int = 1) -> QuotaCheckResult:
        usage = self._quotas.get(extension_id)
        if not usage:
            return QuotaCheckResult(allowed=False, remaining_hourly=0,
                                   remaining_daily=0, burst_available=0,
                                   reason="Extension not registered")
        limits = self._get_limits(extension_id)
        hourly_limit = limits["requests_per_hour"]
        daily_limit = limits["requests_per_day"]
        burst_limit = limits["burst"]

        remaining_h = hourly_limit - usage.hourly_used
        remaining_d = daily_limit - usage.daily_used
        burst_avail = burst_limit - usage.burst_used

        used_burst = False
        if remaining_h >= count and remaining_d >= count:
            usage.hourly_used += count
            usage.daily_used += count
            usage.total_requests += count
        elif burst_avail >= count and remaining_d >= count:
            usage.burst_used += count
            usage.daily_used += count
            usage.total_requests += count
            used_burst = True
        else:
            usage.overage_count += 1
            reason = "Hourly limit exceeded" if remaining_d >= count else "Daily limit exceeded"
            return QuotaCheckResult(
                allowed=False, remaining_hourly=max(0, remaining_h),
                remaining_daily=max(0, remaining_d),
                burst_available=max(0, burst_avail), reason=reason,
            )

        return QuotaCheckResult(
            allowed=True, remaining_hourly=max(0, hourly_limit - usage.hourly_used),
            remaining_daily=max(0, daily_limit - usage.daily_used),
            burst_available=max(0, burst_limit - usage.burst_used),
            used_burst=used_burst,
        )

    def reset_hourly(self, extension_id: str) -> None:
        usage = self._quotas.get(extension_id)
        if usage:
            usage.hourly_used = 0
            usage.burst_used = 0
            usage.last_reset_hour = datetime.now(timezone.utc).isoformat()

    def get_usage(self, extension_id: str) -> dict | None:
        u = self._quotas.get(extension_id)
        if not u:
            return None
        limits = self._get_limits(extension_id)
        return {
            "extension_id": extension_id, "tier": u.tier.value,
            "hourly": {"used": u.hourly_used, "limit": limits["requests_per_hour"]},
            "daily": {"used": u.daily_used, "limit": limits["requests_per_day"]},
            "burst": {"used": u.burst_used, "limit": limits["burst"]},
            "total_requests": u.total_requests, "overage_count": u.overage_count,
        }
