"""Quota Planner — recommend and manage quota tiers for extensions.

Analyzes usage patterns, recommends optimal quota tiers, predicts
overage risk, and provides cost optimization suggestions.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class QuotaTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class TierLimits:
    tier: QuotaTier
    api_calls_per_day: int
    storage_mb: int
    compute_minutes: int
    webhooks: int
    price_cents: int


TIERS: dict[QuotaTier, TierLimits] = {
    QuotaTier.FREE: TierLimits(QuotaTier.FREE, 1000, 100, 10, 5, 0),
    QuotaTier.STARTER: TierLimits(QuotaTier.STARTER, 10000, 1000, 60, 25, 999),
    QuotaTier.PROFESSIONAL: TierLimits(QuotaTier.PROFESSIONAL, 100000, 10000, 300, 100, 4999),
    QuotaTier.ENTERPRISE: TierLimits(QuotaTier.ENTERPRISE, 1000000, 100000, 1440, 500, 19999),
}


@dataclass
class UsageSnapshot:
    api_calls_per_day: int = 0
    storage_mb: int = 0
    compute_minutes: int = 0
    webhooks: int = 0


class QuotaPlanner:
    """Recommends and manages quota tiers based on usage."""

    def __init__(self):
        self._usage: dict[str, list[UsageSnapshot]] = {}
        self._assigned: dict[str, QuotaTier] = {}

    def record_usage(self, org_id: str, snapshot: UsageSnapshot) -> None:
        self._usage.setdefault(org_id, []).append(snapshot)

    def assign_tier(self, org_id: str, tier: QuotaTier) -> TierLimits:
        self._assigned[org_id] = tier
        return TIERS[tier]

    def get_tier(self, org_id: str) -> QuotaTier:
        return self._assigned.get(org_id, QuotaTier.FREE)

    def recommend_tier(self, org_id: str) -> dict:
        """Recommend the best tier based on recent usage."""
        snapshots = self._usage.get(org_id, [])
        if not snapshots:
            return {"recommended": QuotaTier.FREE.value, "reason": "No usage data"}

        # Use peak values from recent snapshots
        peak = UsageSnapshot(
            api_calls_per_day=max(s.api_calls_per_day for s in snapshots),
            storage_mb=max(s.storage_mb for s in snapshots),
            compute_minutes=max(s.compute_minutes for s in snapshots),
            webhooks=max(s.webhooks for s in snapshots),
        )

        for tier in [QuotaTier.FREE, QuotaTier.STARTER, QuotaTier.PROFESSIONAL, QuotaTier.ENTERPRISE]:
            limits = TIERS[tier]
            if (peak.api_calls_per_day <= limits.api_calls_per_day
                and peak.storage_mb <= limits.storage_mb
                and peak.compute_minutes <= limits.compute_minutes
                and peak.webhooks <= limits.webhooks):
                return {
                    "recommended": tier.value,
                    "price_cents": limits.price_cents,
                    "reason": f"Peak usage fits within {tier.value} limits",
                    "headroom_pct": self._calc_headroom(peak, limits),
                }

        return {"recommended": QuotaTier.ENTERPRISE.value, "reason": "Usage exceeds all standard tiers"}

    def predict_overage(self, org_id: str) -> dict:
        """Predict if current tier will be exceeded."""
        tier = self.get_tier(org_id)
        limits = TIERS[tier]
        snapshots = self._usage.get(org_id, [])
        if not snapshots:
            return {"at_risk": False, "metrics": {}}

        peak = UsageSnapshot(
            api_calls_per_day=max(s.api_calls_per_day for s in snapshots),
            storage_mb=max(s.storage_mb for s in snapshots),
            compute_minutes=max(s.compute_minutes for s in snapshots),
            webhooks=max(s.webhooks for s in snapshots),
        )

        metrics = {
            "api_calls": {"used": peak.api_calls_per_day, "limit": limits.api_calls_per_day,
                          "pct": round(peak.api_calls_per_day / max(1, limits.api_calls_per_day) * 100, 1)},
            "storage": {"used": peak.storage_mb, "limit": limits.storage_mb,
                        "pct": round(peak.storage_mb / max(1, limits.storage_mb) * 100, 1)},
        }
        at_risk = any(m["pct"] > 80 for m in metrics.values())
        return {"at_risk": at_risk, "tier": tier.value, "metrics": metrics}

    def get_savings(self, org_id: str) -> dict | None:
        """Check if org could save by downgrading."""
        current = self.get_tier(org_id)
        rec = self.recommend_tier(org_id)
        rec_tier = QuotaTier(rec["recommended"])
        current_price = TIERS[current].price_cents
        rec_price = TIERS[rec_tier].price_cents
        if rec_price < current_price:
            return {"current_tier": current.value, "recommended": rec_tier.value,
                    "monthly_savings_cents": current_price - rec_price}
        return None

    def _calc_headroom(self, usage: UsageSnapshot, limits: TierLimits) -> int:
        pcts = [
            usage.api_calls_per_day / max(1, limits.api_calls_per_day),
            usage.storage_mb / max(1, limits.storage_mb),
        ]
        return round((1 - max(pcts)) * 100)
