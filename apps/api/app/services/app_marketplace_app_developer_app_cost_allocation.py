"""Cost allocation — attribute infrastructure costs to individual apps."""

from collections import defaultdict


def allocate_costs(*, apps: list[dict], total_cost_cents: int) -> list[dict]:
    total_usage = sum(a.get("usage_units", 0) for a in apps)
    if total_usage == 0:
        per_app = total_cost_cents // max(len(apps), 1)
        return [{"app_id": a["id"], "cost_cents": per_app, "pct": round(100 / max(len(apps), 1), 1)} for a in apps]
    result = []
    for a in apps:
        pct = a.get("usage_units", 0) / total_usage
        result.append({"app_id": a["id"], "cost_cents": round(total_cost_cents * pct),
                        "pct": round(pct * 100, 1), "usage_units": a.get("usage_units", 0)})
    return sorted(result, key=lambda r: -r["cost_cents"])


def compute_cost_trend(*, monthly_costs: list[dict]) -> dict:
    if len(monthly_costs) < 2:
        return {"trend": "stable", "change_pct": 0}
    latest = monthly_costs[-1].get("total_cents", 0)
    previous = monthly_costs[-2].get("total_cents", 0)
    if previous == 0:
        return {"trend": "up" if latest > 0 else "stable", "change_pct": 0}
    change = round((latest - previous) / previous * 100, 1)
    return {"trend": "up" if change > 5 else "down" if change < -5 else "stable", "change_pct": change}


def build_cost_report(*, allocations: list[dict], period: str, total_cents: int) -> dict:
    return {"period": period, "total": f"${total_cents / 100:,.2f}", "total_cents": total_cents,
            "app_count": len(allocations), "allocations": allocations,
            "top_spender": allocations[0]["app_id"] if allocations else None}
