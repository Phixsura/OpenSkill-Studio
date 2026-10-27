"""App Usage Metering — track API consumption per app installation.

Provides per-installation usage tracking for the developer platform:
- Request counting per endpoint/method/hour
- Bandwidth tracking (request + response bytes)
- Rate limit quota management with sliding window
- Usage aggregation by hour/day/month
- Overage detection and throttle recommendations
- Export-ready usage reports per billing period
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class MeterType(str, Enum):
    API_REQUEST = "api_request"
    BANDWIDTH_IN = "bandwidth_in"
    BANDWIDTH_OUT = "bandwidth_out"
    WEBHOOK_DELIVERY = "webhook_delivery"
    SANDBOX_EXECUTION = "sandbox_execution"
    STORAGE_BYTES = "storage_bytes"


class QuotaTier(str, Enum):
    FREE = "free"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


# ── Quota limits per tier ────────────────────────────────

QUOTA_LIMITS: dict[QuotaTier, dict[MeterType, int]] = {
    QuotaTier.FREE: {
        MeterType.API_REQUEST: 1_000,         # per hour
        MeterType.BANDWIDTH_IN: 10_485_760,    # 10 MB per hour
        MeterType.BANDWIDTH_OUT: 52_428_800,   # 50 MB per hour
        MeterType.WEBHOOK_DELIVERY: 100,       # per hour
        MeterType.SANDBOX_EXECUTION: 50,       # per hour
        MeterType.STORAGE_BYTES: 104_857_600,  # 100 MB total
    },
    QuotaTier.STANDARD: {
        MeterType.API_REQUEST: 10_000,
        MeterType.BANDWIDTH_IN: 104_857_600,
        MeterType.BANDWIDTH_OUT: 524_288_000,
        MeterType.WEBHOOK_DELIVERY: 1_000,
        MeterType.SANDBOX_EXECUTION: 500,
        MeterType.STORAGE_BYTES: 1_073_741_824,
    },
    QuotaTier.PROFESSIONAL: {
        MeterType.API_REQUEST: 100_000,
        MeterType.BANDWIDTH_IN: 1_073_741_824,
        MeterType.BANDWIDTH_OUT: 5_368_709_120,
        MeterType.WEBHOOK_DELIVERY: 10_000,
        MeterType.SANDBOX_EXECUTION: 5_000,
        MeterType.STORAGE_BYTES: 10_737_418_240,
    },
    QuotaTier.ENTERPRISE: {
        MeterType.API_REQUEST: 1_000_000,
        MeterType.BANDWIDTH_IN: 10_737_418_240,
        MeterType.BANDWIDTH_OUT: 53_687_091_200,
        MeterType.WEBHOOK_DELIVERY: 100_000,
        MeterType.SANDBOX_EXECUTION: 50_000,
        MeterType.STORAGE_BYTES: 107_374_182_400,
    },
}


@dataclass
class UsageRecord:
    """A single metered usage event."""

    installation_id: str
    meter_type: MeterType
    value: int  # count or bytes
    endpoint: str | None = None
    method: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class HourlyBucket:
    """Aggregated usage for one installation + meter type + hour."""

    installation_id: str
    meter_type: MeterType
    hour_key: str  # "2026-10-28T14" format
    total: int = 0
    count: int = 0  # number of records in this bucket
    peak: int = 0


@dataclass
class QuotaCheckResult:
    """Result of a quota check."""

    allowed: bool
    meter_type: MeterType
    current_usage: int
    limit: int
    remaining: int
    usage_pct: float
    throttle_recommended: bool = False
    overage: int = 0


def hour_key(dt: datetime) -> str:
    """Format a datetime as an hourly bucket key."""
    return dt.strftime("%Y-%m-%dT%H")


def day_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


class AppUsageMeter:
    """In-memory usage metering engine.

    Production deployments should back this with Redis sorted sets or
    a time-series table. This implementation provides the core algorithm
    and is suitable for single-process or test environments.
    """

    def __init__(self, default_tier: QuotaTier = QuotaTier.FREE):
        self.default_tier = default_tier
        # installation_id → tier
        self._tiers: dict[str, QuotaTier] = {}
        # (installation_id, meter_type, hour_key) → HourlyBucket
        self._hourly: dict[tuple[str, MeterType, str], HourlyBucket] = {}
        # Per-endpoint counters: (installation_id, hour_key, method, endpoint) → count
        self._endpoint_counters: dict[tuple[str, str, str, str], int] = defaultdict(int)

    def set_tier(self, installation_id: str, tier: QuotaTier) -> None:
        self._tiers[installation_id] = tier

    def get_tier(self, installation_id: str) -> QuotaTier:
        return self._tiers.get(installation_id, self.default_tier)

    # ── Recording ────────────────────────────────────────

    def record(self, record: UsageRecord) -> QuotaCheckResult:
        """Record a usage event and return quota status.

        Returns the quota check result AFTER recording the usage.
        Callers should check `result.allowed` before proceeding.
        """
        hk = hour_key(record.timestamp)
        bucket_key = (record.installation_id, record.meter_type, hk)

        bucket = self._hourly.get(bucket_key)
        if bucket is None:
            bucket = HourlyBucket(
                installation_id=record.installation_id,
                meter_type=record.meter_type,
                hour_key=hk,
            )
            self._hourly[bucket_key] = bucket

        bucket.total += record.value
        bucket.count += 1
        bucket.peak = max(bucket.peak, record.value)

        # Track per-endpoint
        if record.endpoint and record.method:
            ep_key = (record.installation_id, hk, record.method, record.endpoint)
            self._endpoint_counters[ep_key] += record.value

        return self.check_quota(record.installation_id, record.meter_type, record.timestamp)

    # ── Quota checks ─────────────────────────────────────

    def check_quota(self, installation_id: str, meter_type: MeterType,
                    now: datetime | None = None) -> QuotaCheckResult:
        """Check current usage against the installation's quota tier."""
        now = now or datetime.now(UTC)
        tier = self.get_tier(installation_id)
        limits = QUOTA_LIMITS.get(tier, QUOTA_LIMITS[QuotaTier.FREE])
        limit = limits.get(meter_type, 0)

        # Storage is a total limit, not per-hour
        if meter_type == MeterType.STORAGE_BYTES:
            current = self._total_usage(installation_id, meter_type)
        else:
            current = self._hourly_usage(installation_id, meter_type, now)

        remaining = max(0, limit - current)
        usage_pct = (current / limit * 100) if limit > 0 else 100.0
        overage = max(0, current - limit)

        return QuotaCheckResult(
            allowed=current <= limit,
            meter_type=meter_type,
            current_usage=current,
            limit=limit,
            remaining=remaining,
            usage_pct=round(usage_pct, 2),
            throttle_recommended=usage_pct >= 80.0,
            overage=overage,
        )

    # ── Aggregation ──────────────────────────────────────

    def hourly_usage(self, installation_id: str, meter_type: MeterType,
                     now: datetime | None = None) -> int:
        """Get current hour's usage."""
        now = now or datetime.now(UTC)
        return self._hourly_usage(installation_id, meter_type, now)

    def daily_usage(self, installation_id: str, meter_type: MeterType,
                    date: datetime | None = None) -> int:
        """Get total usage for a calendar day (UTC)."""
        date = date or datetime.now(UTC)
        dk = day_key(date)
        total = 0
        for (inst_id, mt, hk), bucket in self._hourly.items():
            if inst_id == installation_id and mt == meter_type and hk.startswith(dk):
                total += bucket.total
        return total

    def monthly_usage(self, installation_id: str, meter_type: MeterType,
                      date: datetime | None = None) -> int:
        """Get total usage for a calendar month (UTC)."""
        date = date or datetime.now(UTC)
        mk = month_key(date)
        total = 0
        for (inst_id, mt, hk), bucket in self._hourly.items():
            if inst_id == installation_id and mt == meter_type and hk.startswith(mk):
                total += bucket.total
        return total

    def top_endpoints(self, installation_id: str, hour: datetime | None = None,
                      limit: int = 10) -> list[dict]:
        """Top endpoints by request count for the given hour."""
        hour = hour or datetime.now(UTC)
        hk = hour_key(hour)
        entries: list[tuple[str, str, int]] = []
        for (inst_id, h, method, endpoint), count in self._endpoint_counters.items():
            if inst_id == installation_id and h == hk:
                entries.append((method, endpoint, count))
        entries.sort(key=lambda x: x[2], reverse=True)
        return [
            {"method": m, "endpoint": e, "count": c}
            for m, e, c in entries[:limit]
        ]

    def usage_report(self, installation_id: str, now: datetime | None = None) -> dict:
        """Generate a usage report for all meter types."""
        now = now or datetime.now(UTC)
        tier = self.get_tier(installation_id)
        report = {
            "installation_id": installation_id,
            "tier": tier.value,
            "generated_at": now.isoformat(),
            "meters": {},
        }
        for meter_type in MeterType:
            quota = self.check_quota(installation_id, meter_type, now)
            report["meters"][meter_type.value] = {
                "current_hour": self._hourly_usage(installation_id, meter_type, now),
                "today": self.daily_usage(installation_id, meter_type, now),
                "this_month": self.monthly_usage(installation_id, meter_type, now),
                "limit_per_hour": quota.limit,
                "usage_pct": quota.usage_pct,
                "remaining": quota.remaining,
                "allowed": quota.allowed,
            }
        return report

    # ── Internals ────────────────────────────────────────

    def _hourly_usage(self, installation_id: str, meter_type: MeterType,
                      now: datetime) -> int:
        hk = hour_key(now)
        bucket = self._hourly.get((installation_id, meter_type, hk))
        return bucket.total if bucket else 0

    def _total_usage(self, installation_id: str, meter_type: MeterType) -> int:
        """Sum all-time usage for a meter type (used for storage quotas)."""
        total = 0
        for (inst_id, mt, _), bucket in self._hourly.items():
            if inst_id == installation_id and mt == meter_type:
                total += bucket.total
        return total
