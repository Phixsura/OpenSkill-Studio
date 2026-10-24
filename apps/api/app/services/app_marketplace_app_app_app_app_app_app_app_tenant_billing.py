"""Tenant billing tracker — track per-tenant resource usage and billing."""
from __future__ import annotations
from collections import defaultdict


def calculate_bill(usage: list[dict], rates: dict[str, float]) -> dict:
    by_resource: dict[str, dict] = defaultdict(lambda: {"quantity": 0, "cost": 0})
    for item in usage:
        resource = item["resource"]
        qty = item["quantity"]
        rate = rates.get(resource, 0)
        cost = round(qty * rate, 2)
        by_resource[resource]["quantity"] += qty
        by_resource[resource]["cost"] += cost
    total = round(sum(r["cost"] for r in by_resource.values()), 2)
    line_items = [{"resource": k, "quantity": v["quantity"],
                   "rate": rates.get(k, 0), "cost": round(v["cost"], 2)}
                  for k, v in sorted(by_resource.items())]
    return {"total": total, "line_items": line_items, "currency": "USD"}


def usage_summary(tenants: list[dict]) -> dict:
    total_cost = sum(t.get("total", 0) for t in tenants)
    top = sorted(tenants, key=lambda t: -t.get("total", 0))[:5]
    return {"total_cost": round(total_cost, 2), "tenant_count": len(tenants),
            "top_spenders": [{"tenant": t["tenant_id"], "cost": t["total"]} for t in top]}
