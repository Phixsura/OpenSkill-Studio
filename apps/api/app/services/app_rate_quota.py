"""App Rate Quota — tiered rate limiting based on subscription plans.

Maps subscription tiers to rate limits:
- Define tier quotas (free, starter, pro, enterprise)
- Look up limits by tier
- Compute overage and remaining
- Tier upgrade recommendations
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class TierQuota:
    """Rate quota for a subscription tier."""

    tier: str
    requests_per_day: int
    requests_per_minute: int
    storage_mb: int
    webhooks: int
    priority: int = 0  # for ordering (0 = lowest)


@dataclass
class QuotaCheck:
    """Result of checking usage against a tier's quota."""

    metric: str
    used: float
    limit: float
    remaining: float
    exceeded: bool
    overage: float


class AppRateQuota:
    """Tiered rate limiting based on subscription plans."""

    def __init__(self) -> None:
        self._tiers: dict[str, TierQuota] = {}

    def define_tier(self, quota: TierQuota) -> None:
        """Define or update a tier's quotas."""
        if not quota.tier:
            raise ValueError("tier is required")
        self._tiers[quota.tier] = quota

    def get_tier(self, tier: str) -> TierQuota:
        """Get a tier's quota config."""
        quota = self._tiers.get(tier)
        if quota is None:
            raise KeyError(f"Tier {tier} not found")
        return quota

    def list_tiers(self) -> list[TierQuota]:
        """List all tiers sorted by priority."""
        return sorted(self._tiers.values(), key=lambda t: t.priority)

    def check_usage(
        self, tier: str, metric: str, used: float
    ) -> QuotaCheck:
        """Check usage against a tier's limit for a metric."""
        quota = self.get_tier(tier)
        limit_map: dict[str, float] = {
            "requests_per_day": float(quota.requests_per_day),
            "requests_per_minute": float(quota.requests_per_minute),
            "storage_mb": float(quota.storage_mb),
            "webhooks": float(quota.webhooks),
        }

        limit = limit_map.get(metric)
        if limit is None:
            raise ValueError(f"Unknown metric: {metric}")

        remaining = max(0.0, limit - used)
        overage = max(0.0, used - limit)
        return QuotaCheck(
            metric=metric,
            used=used,
            limit=limit,
            remaining=remaining,
            exceeded=used > limit,
            overage=overage,
        )

    def recommend_upgrade(
        self, current_tier: str, metric: str, needed: float
    ) -> str | None:
        """Recommend the lowest tier that accommodates the needed capacity."""
        limit_map_key = metric
        tiers = self.list_tiers()

        current = self._tiers.get(current_tier)
        if current is None:
            return None

        # Check if current tier already sufficient
        current_val = getattr(current, limit_map_key, None)
        if current_val is not None and current_val >= needed:
            return None

        for t in tiers:
            if t.priority <= current.priority:
                continue
            quota_val = getattr(t, limit_map_key, None)
            if quota_val is not None and quota_val >= needed:
                return t.tier

        return None
