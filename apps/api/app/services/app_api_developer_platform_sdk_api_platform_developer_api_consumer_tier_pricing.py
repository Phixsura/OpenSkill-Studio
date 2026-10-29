"""API Consumer Tier Pricing — tiered pricing for API consumption."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class PricingTier:
    tier_id: str
    name: str  # "free", "starter", "pro", "enterprise"
    monthly_limit: int
    price_per_request_cents: float  # overage price
    base_price_cents: int = 0
    features: list[str] = field(default_factory=list)

@dataclass
class ConsumerBilling:
    consumer_id: str
    tier_id: str
    usage_this_month: int = 0
    overage_cost_cents: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerTierPricing:
    def __init__(self) -> None:
        self._tiers: dict[tuple[str, str], PricingTier] = {}
        self._billing: dict[tuple[str, str], ConsumerBilling] = {}

    def create_tier(self, installation_id: str, tier: PricingTier) -> PricingTier:
        if not installation_id: raise ValueError("installation_id is required")
        if tier.monthly_limit < 0: raise ValueError("monthly_limit must be non-negative")
        if tier.price_per_request_cents < 0: raise ValueError("price must be non-negative")
        if tier.base_price_cents < 0: raise ValueError("base_price must be non-negative")
        key = (installation_id, tier.tier_id)
        if key in self._tiers: raise ValueError(f"Tier {tier.tier_id} already exists")
        self._tiers[key] = tier
        return tier

    def assign_tier(self, installation_id: str, consumer_id: str, tier_id: str) -> ConsumerBilling:
        if (installation_id, tier_id) not in self._tiers: raise KeyError(f"Tier {tier_id} not found")
        billing = ConsumerBilling(consumer_id=consumer_id, tier_id=tier_id)
        self._billing[(installation_id, consumer_id)] = billing
        return billing

    def record_usage(self, installation_id: str, consumer_id: str, requests: int) -> ConsumerBilling:
        key = (installation_id, consumer_id)
        billing = self._billing.get(key)
        if billing is None: raise KeyError(f"No billing for {consumer_id}")
        if not isinstance(requests, int) or isinstance(requests, bool) or requests < 1:
            raise ValueError("requests must be positive integer")
        tier = self._tiers.get((installation_id, billing.tier_id))
        if tier is None: raise KeyError(f"Tier {billing.tier_id} not found")
        billing.usage_this_month += requests
        if billing.usage_this_month > tier.monthly_limit:
            overage = billing.usage_this_month - tier.monthly_limit
            billing.overage_cost_cents = round(overage * tier.price_per_request_cents, 2)
        return billing

    def get_invoice(self, installation_id: str, consumer_id: str) -> dict[str, object]:
        billing = self._billing.get((installation_id, consumer_id))
        if billing is None: raise KeyError(f"No billing for {consumer_id}")
        tier = self._tiers.get((installation_id, billing.tier_id))
        base = tier.base_price_cents if tier else 0
        return {"consumer_id": consumer_id, "tier": billing.tier_id, "base_cents": base, "overage_cents": billing.overage_cost_cents, "total_cents": base + billing.overage_cost_cents, "usage": billing.usage_this_month}

    def list_tiers(self, installation_id: str) -> list[PricingTier]:
        return [t for (inst, _), t in self._tiers.items() if inst == installation_id]
