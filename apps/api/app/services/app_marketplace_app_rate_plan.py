"""Rate plan — usage-based pricing with metered billing."""


def calculate_usage_cost(*, plan: dict, usage: dict) -> dict:
    line_items = []
    total = 0.0
    # Base fee
    base = plan.get("base_fee", 0)
    if base > 0:
        line_items.append({"item": "Base fee", "quantity": 1, "unit_price": base, "total": base})
        total += base
    # Metered dimensions
    for dim in plan.get("dimensions", []):
        qty = usage.get(dim["key"], 0)
        free_tier = dim.get("free_tier", 0)
        billable = max(qty - free_tier, 0)
        cost = round(billable * dim["unit_price"], 4)
        line_items.append({
            "item": dim["label"],
            "quantity": qty,
            "free_tier": free_tier,
            "billable": billable,
            "unit_price": dim["unit_price"],
            "total": round(cost, 2),
        })
        total += cost
    return {"line_items": line_items, "subtotal": round(total, 2),
            "currency": plan.get("currency", "USD")}


def compare_plans(*, plans: list[dict], usage: dict) -> dict:
    results = []
    for p in plans:
        cost = calculate_usage_cost(plan=p, usage=usage)
        results.append({"plan_name": p["name"], "cost": cost["subtotal"]})
    results.sort(key=lambda x: x["cost"])
    cheapest = results[0]["plan_name"] if results else None
    return {"comparisons": results, "recommended": cheapest}
