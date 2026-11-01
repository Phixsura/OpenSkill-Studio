"""Cost estimator — estimate monthly costs based on usage."""
from __future__ import annotations

PRICING = {
    "api_calls": {"unit": "per 1K calls", "free": 0, "pro": 0.50, "enterprise": 0.30},
    "storage_gb": {"unit": "per GB", "free": 0, "pro": 0.10, "enterprise": 0.07},
    "bandwidth_gb": {"unit": "per GB", "free": 0, "pro": 0.08, "enterprise": 0.05},
    "compute_hrs": {"unit": "per hour", "free": 0, "pro": 0.25, "enterprise": 0.15},
}
BASE_PRICE = {"free": 0, "pro": 29.0, "enterprise": 99.0}


def estimate_cost(plan: str, usage: dict[str, float]) -> dict:
    base = BASE_PRICE.get(plan, 0)
    line_items = []
    variable_total = 0.0
    for resource, amount in usage.items():
        if resource in PRICING:
            rate = PRICING[resource].get(plan, 0)
            cost = round(amount * rate, 2)
            variable_total += cost
            line_items.append({"resource": resource, "amount": amount,
                              "rate": rate, "cost": cost, "unit": PRICING[resource]["unit"]})
    total = round(base + variable_total, 2)
    return {"plan": plan, "base_price": base, "variable_cost": round(variable_total, 2),
            "total": total, "line_items": line_items,
            "display": f"${total:.2f}/mo"}


def compare_plans(usage: dict[str, float]) -> list[dict]:
    return [estimate_cost(p, usage) for p in ("free", "pro", "enterprise")]
