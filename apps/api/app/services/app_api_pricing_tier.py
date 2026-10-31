"""App API Pricing Tier — manage pricing plans with feature access.

Manages pricing tiers:
- Define tiers with features and limits
- Assign tenants to tiers
- Check feature access by tier
- Per-installation scoped tiers
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class PricingTier:
    """A pricing tier."""

    tier_id: str
    name: str
    price_monthly: float
    features: set[str] = field(default_factory=set)
    rate_limit: int = 1000  # requests/min
    sort_order: int = 0


class AppAPIPricingTier:
    """Manage pricing plans with feature access."""

    def __init__(self) -> None:
        self._tiers: dict[tuple[str, str], PricingTier] = {}
        self._assignments: dict[tuple[str, str], str] = {}  # (inst, tenant) → tier_id

    def create_tier(
        self, installation_id: str, tier_id: str, name: str,
        price_monthly: float, features: list[str],
        rate_limit: int = 1000, sort_order: int = 0,
    ) -> PricingTier:
        if not installation_id:
            raise ValueError("installation_id is required")
        if price_monthly < 0:
            raise ValueError("price must be non-negative")

        tier = PricingTier(
            tier_id=tier_id, name=name, price_monthly=price_monthly,
            features=set(features), rate_limit=rate_limit, sort_order=sort_order,
        )
        self._tiers[(installation_id, tier_id)] = tier
        return tier

    def assign_tier(self, installation_id: str, tenant_id: str, tier_id: str) -> None:
        if (installation_id, tier_id) not in self._tiers:
            raise KeyError(f"Tier {tier_id} not found")
        self._assignments[(installation_id, tenant_id)] = tier_id

    def has_feature(self, installation_id: str, tenant_id: str, feature: str) -> bool:
        tier_id = self._assignments.get((installation_id, tenant_id))
        if tier_id is None:
            return False
        tier = self._tiers.get((installation_id, tier_id))
        return tier is not None and feature in tier.features

    def tenant_tier(self, installation_id: str, tenant_id: str) -> PricingTier | None:
        tier_id = self._assignments.get((installation_id, tenant_id))
        if tier_id is None:
            return None
        return self._tiers.get((installation_id, tier_id))

    def list_tiers(self, installation_id: str) -> list[PricingTier]:
        tiers = [t for (inst, _), t in self._tiers.items() if inst == installation_id]
        return sorted(tiers, key=lambda t: t.sort_order)
