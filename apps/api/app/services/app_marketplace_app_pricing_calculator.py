"""Pricing calculator — compute costs for marketplace platform fees."""


PLATFORM_FEE_TIERS = [
    {"min_revenue": 0, "max_revenue": 10000, "fee_pct": 30},
    {"min_revenue": 10000, "max_revenue": 100000, "fee_pct": 20},
    {"min_revenue": 100000, "max_revenue": float("inf"), "fee_pct": 15},
]


def calculate_platform_fee(*, gross_revenue: float) -> dict:
    if gross_revenue < 0:
        return {"error": "Revenue cannot be negative"}
    total_fee = 0.0
    breakdown = []
    remaining = gross_revenue
    for tier in PLATFORM_FEE_TIERS:
        if remaining <= 0:
            break
        tier_max = tier["max_revenue"] - tier["min_revenue"]
        taxable = min(remaining, tier_max)
        fee = round(taxable * tier["fee_pct"] / 100, 2)
        breakdown.append({
            "range": f"${tier['min_revenue']:,.0f}–${tier['max_revenue']:,.0f}" if tier["max_revenue"] != float("inf") else f"${tier['min_revenue']:,.0f}+",
            "rate": tier["fee_pct"],
            "taxable_amount": round(taxable, 2),
            "fee": fee,
        })
        total_fee += fee
        remaining -= taxable
    net = round(gross_revenue - total_fee, 2)
    effective_rate = round(total_fee / max(gross_revenue, 0.01) * 100, 2)
    return {
        "gross_revenue": gross_revenue,
        "total_fee": round(total_fee, 2),
        "net_revenue": net,
        "effective_rate": effective_rate,
        "breakdown": breakdown,
    }
