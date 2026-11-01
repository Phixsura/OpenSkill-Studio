"""Infrastructure cost report — generate monthly infra cost reports."""
from __future__ import annotations


def generate_cost_report(costs: dict[str, dict]) -> dict:
    items = []
    total = 0
    for category, data in costs.items():
        amount = data.get("amount", 0)
        total += amount
        items.append({"category": category, "amount": amount,
                       "change_pct": data.get("change_pct", 0),
                       "forecast": data.get("forecast", amount)})
    items.sort(key=lambda x: -x["amount"])
    forecast_total = sum(i["forecast"] for i in items)
    return {"items": items, "total": round(total, 2), "category_count": len(items),
            "forecast_total": round(forecast_total, 2),
            "display_total": f"${total:,.2f}",
            "top_category": items[0]["category"] if items else None}
