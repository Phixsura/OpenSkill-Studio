"""API usage billing calculator — metered billing based on API call volumes."""
from __future__ import annotations


TIERS = [
    {"limit": 10000, "price_per_call": 0.0},         # free tier
    {"limit": 100000, "price_per_call": 0.001},       # $1/1K calls
    {"limit": 1000000, "price_per_call": 0.0005},     # $0.50/1K calls
    {"limit": float("inf"), "price_per_call": 0.0002}, # $0.20/1K calls
]


def calculate_bill(*, api_calls: int, storage_gb: float = 0,
                     storage_price_per_gb: float = 0.10,
                     base_price: float = 0) -> dict:
    api_cost = 0.0
    remaining = api_calls
    breakdown = []
    prev_limit = 0
    for tier in TIERS:
        tier_size = tier["limit"] - prev_limit if tier["limit"] != float("inf") else remaining
        used = min(remaining, tier_size)
        if used <= 0:
            break
        cost = used * tier["price_per_call"]
        breakdown.append({"range": f"{prev_limit:,}-{prev_limit + used:,}",
                           "calls": used, "rate": tier["price_per_call"],
                           "cost": round(cost, 2)})
        api_cost += cost
        remaining -= used
        prev_limit = int(tier["limit"]) if tier["limit"] != float("inf") else prev_limit + used
    storage_cost = round(storage_gb * storage_price_per_gb, 2)
    total = round(base_price + api_cost + storage_cost, 2)
    return {
        "api_calls": api_calls, "api_cost": round(api_cost, 2),
        "storage_gb": storage_gb, "storage_cost": storage_cost,
        "base_price": base_price, "total": total,
        "total_display": f"${total:,.2f}",
        "breakdown": breakdown,
    }
