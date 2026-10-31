"""Revenue tracker — MRR, ARR, and revenue breakdown for paid apps."""

from collections import defaultdict


def compute_mrr(*, subscriptions: list[dict]) -> dict:
    total = 0
    by_plan = defaultdict(int)
    for sub in subscriptions:
        if sub.get("status") == "active":
            monthly = sub.get("monthly_amount_cents", 0)
            total += monthly
            by_plan[sub.get("plan", "unknown")] += monthly
    return {"mrr_cents": total, "arr_cents": total * 12,
            "by_plan": dict(sorted(by_plan.items(), key=lambda x: -x[1]))}


def compute_revenue_growth(*, current_mrr: int, previous_mrr: int) -> dict:
    if previous_mrr == 0:
        return {"growth_pct": 100 if current_mrr > 0 else 0, "direction": "up" if current_mrr > 0 else "flat"}
    change = round((current_mrr - previous_mrr) / previous_mrr * 100, 1)
    return {"growth_pct": change, "direction": "up" if change > 0 else "down" if change < 0 else "flat"}


def build_revenue_summary(*, mrr_cents: int, total_customers: int, churn_rate: float) -> dict:
    arpu = round(mrr_cents / max(total_customers, 1))
    ltv = round(arpu / max(churn_rate / 100, 0.01))
    return {
        "mrr": f"${mrr_cents / 100:,.2f}", "arr": f"${mrr_cents * 12 / 100:,.2f}",
        "arpu": f"${arpu / 100:,.2f}", "estimated_ltv": f"${ltv / 100:,.2f}",
        "customers": total_customers,
    }
