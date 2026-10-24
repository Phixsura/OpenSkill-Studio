"""App pricing calculator — compute pricing for marketplace apps."""
from __future__ import annotations


def calculate_pricing(*, base_price: float, usage_units: int,
                        price_per_unit: float = 0, discount_pct: float = 0,
                        billing_period: str = "monthly") -> dict:
    usage_cost = usage_units * price_per_unit
    subtotal = base_price + usage_cost
    discount = round(subtotal * discount_pct / 100, 2)
    total = round(subtotal - discount, 2)
    annual = total * 12 if billing_period == "monthly" else total
    return {
        "base_price": base_price, "usage_cost": round(usage_cost, 2),
        "subtotal": round(subtotal, 2), "discount": discount,
        "discount_pct": discount_pct, "total": total,
        "total_display": f"${total:,.2f}/{billing_period[:2]}",
        "annual_estimate": round(annual, 2),
        "annual_display": f"${annual:,.2f}/yr",
        "billing_period": billing_period,
    }


def compare_plans(plans: list[dict]) -> dict:
    results = [calculate_pricing(**p) for p in plans]
    cheapest = min(results, key=lambda r: r["annual_estimate"])
    return {"plans": results, "cheapest_annual": cheapest["annual_estimate"],
            "plan_count": len(results)}
