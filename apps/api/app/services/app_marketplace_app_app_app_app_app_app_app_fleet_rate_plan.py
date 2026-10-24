"""Fleet rate plan — track API rate plan usage by tier."""
from __future__ import annotations
def fleet_rate_plan(tenants: list[dict]) -> dict:
    by_tier: dict[str, int] = {}
    for t in tenants:
        tier = t.get("tier", "free")
        by_tier[tier] = by_tier.get(tier, 0) + 1
    return {"total": len(tenants), "by_tier": by_tier, "tiers": len(by_tier)}
