"""Revenue analytics — MRR trends, churn analysis, and revenue forecasting."""


def compute_mrr_trend(*, monthly_mrr: list[dict]) -> dict:
    if len(monthly_mrr) < 2:
        return {"trend": "stable", "change_pct": 0}
    latest = monthly_mrr[-1].get("mrr_cents", 0)
    prev = monthly_mrr[-2].get("mrr_cents", 0)
    change_pct = round((latest - prev) / max(prev, 1) * 100, 1)
    return {"trend": "growing" if change_pct > 5 else "declining" if change_pct < -5 else "stable",
            "change_pct": change_pct, "latest_mrr": latest, "previous_mrr": prev}


def compute_revenue_by_plan(*, subscriptions: list[dict]) -> list[dict]:
    by_plan: dict[str, int] = {}
    for s in subscriptions:
        plan = s.get("plan", "unknown")
        by_plan[plan] = by_plan.get(plan, 0) + s.get("monthly_cents", 0)
    return [{"plan": p, "revenue_cents": r, "pct": 0} for p, r in sorted(by_plan.items(), key=lambda x: -x[1])]


def forecast_revenue(*, current_mrr: int, growth_rate_pct: float, months: int = 12) -> list[dict]:
    forecast = []
    mrr = current_mrr
    for m in range(1, months + 1):
        mrr = int(mrr * (1 + growth_rate_pct / 100))
        forecast.append({"month": m, "projected_mrr_cents": mrr})
    return forecast
