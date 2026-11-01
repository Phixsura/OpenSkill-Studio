"""Revenue dashboard — MRR, ARR, and revenue analytics."""


def build_revenue_dashboard(*, mrr: float, arr: float, prev_mrr: float = 0,
                               subscribers: int = 0, churn_rate: float = 0,
                               revenue_by_plan: dict | None = None) -> dict:
    growth = round((mrr - prev_mrr) / max(prev_mrr, 1) * 100, 1) if prev_mrr else 0
    arpu = round(mrr / max(subscribers, 1), 2)
    by_plan = revenue_by_plan or {}
    return {
        "mrr": mrr, "mrr_display": f"${mrr:,.2f}",
        "arr": arr, "arr_display": f"${arr:,.2f}",
        "growth_pct": growth, "growth_trend": "up" if growth > 0 else "down" if growth < 0 else "flat",
        "subscribers": subscribers, "arpu": arpu, "arpu_display": f"${arpu:.2f}",
        "churn_rate": churn_rate, "churn_display": f"{churn_rate}%",
        "by_plan": [{"plan": k, "revenue": v, "display": f"${v:,.2f}"}
                     for k, v in sorted(by_plan.items(), key=lambda x: -x[1])],
    }
