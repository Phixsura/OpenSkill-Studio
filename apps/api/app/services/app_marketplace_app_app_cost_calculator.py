"""Cost calculator — usage-based pricing estimator."""

import html


def calculate_cost(*, tiers: list[dict], usage: int) -> dict:
    remaining = usage
    total_cost = 0.0
    breakdown = []
    for tier in sorted(tiers, key=lambda t: t.get("from", 0)):
        t_from = tier.get("from", 0)
        t_to = tier.get("to")  # None = unlimited
        rate = tier.get("rate", 0)
        if remaining <= 0:
            break
        tier_units = min(remaining, (t_to - t_from) if t_to else remaining)
        tier_cost = round(tier_units * rate, 4)
        total_cost += tier_cost
        breakdown.append({
            "tier": html.escape(tier.get("name", f"{t_from}-{t_to or '∞'}")),
            "units": tier_units,
            "rate": rate,
            "cost": round(tier_cost, 2),
        })
        remaining -= tier_units
    return {"usage": usage, "total_cost": round(total_cost, 2),
            "breakdown": breakdown, "tier_count": len(breakdown)}


def estimate_monthly(*, daily_usage: int, tiers: list[dict]) -> dict:
    monthly = daily_usage * 30
    r = calculate_cost(tiers=tiers, usage=monthly)
    r["daily_usage"] = daily_usage
    r["monthly_usage"] = monthly
    return r
