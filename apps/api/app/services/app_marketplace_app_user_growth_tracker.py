"""User growth tracker — track user acquisition, activation, and churn."""


def calculate_growth_metrics(*, periods: list[dict]) -> dict:
    if not periods:
        return {"error": "No data"}
    metrics = []
    for i, p in enumerate(periods):
        new_users = p.get("new_users", 0)
        churned = p.get("churned", 0)
        net = new_users - churned
        total = p.get("total_users", 0)
        growth_rate = round(net / max(total - net, 1) * 100, 1) if total > 0 else 0
        metrics.append({
            "period": p["period"],
            "new_users": new_users,
            "churned": churned,
            "net_growth": net,
            "total_users": total,
            "growth_rate": growth_rate,
        })
    latest = metrics[-1]
    avg_growth = round(sum(m["growth_rate"] for m in metrics) / len(metrics), 1)
    return {
        "metrics": metrics,
        "current_total": latest["total_users"],
        "avg_growth_rate": avg_growth,
        "trend": "growing" if avg_growth > 0 else "shrinking" if avg_growth < 0 else "flat",
    }
