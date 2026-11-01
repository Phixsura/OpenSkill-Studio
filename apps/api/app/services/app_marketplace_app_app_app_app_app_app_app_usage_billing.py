"""Usage billing calculator — metered billing based on consumption."""
from __future__ import annotations


TIERS = [
    {"up_to": 1000, "price_per_unit": 0.00},
    {"up_to": 10000, "price_per_unit": 0.005},
    {"up_to": 100000, "price_per_unit": 0.003},
    {"up_to": None, "price_per_unit": 0.001},
]


def calculate_tiered_cost(usage: int, tiers: list[dict] | None = None) -> dict:
    tiers = tiers or TIERS
    remaining = usage
    total = 0.0
    breakdown = []
    prev_limit = 0
    for tier in tiers:
        limit = tier["up_to"] or float("inf")
        tier_size = limit - prev_limit
        consumed = min(remaining, tier_size)
        if consumed <= 0:
            break
        cost = round(consumed * tier["price_per_unit"], 4)
        total += cost
        breakdown.append({"range": f"{prev_limit+1}-{int(min(limit, prev_limit+consumed))}",
                          "units": int(consumed), "rate": tier["price_per_unit"], "cost": cost})
        remaining -= consumed
        prev_limit = int(limit)
    return {"usage": usage, "total_cost": round(total, 2), "breakdown": breakdown,
            "display": f"${total:,.2f}"}


def project_monthly(daily_usage: int) -> dict:
    monthly = daily_usage * 30
    cost = calculate_tiered_cost(monthly)
    return {"daily_usage": daily_usage, "projected_monthly": monthly,
            "projected_cost": cost["total_cost"], "display": cost["display"]}
