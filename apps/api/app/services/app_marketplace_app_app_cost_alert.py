"""Cost alert — proactive cost monitoring and budget alerts."""


def evaluate_cost_alerts(*, current_spend: float, budget: float,
                           daily_spend: float, days_remaining: int) -> dict:
    pct_used = round(current_spend / max(budget, 0.01) * 100, 1)
    projected = round(current_spend + daily_spend * days_remaining, 2)
    projected_overage = round(max(projected - budget, 0), 2)
    alerts = []
    if pct_used >= 100:
        alerts.append({"level": "critical", "message": f"Budget exceeded by ${current_spend - budget:.2f}"})
    elif pct_used >= 90:
        alerts.append({"level": "warning", "message": f"90% of budget consumed (${current_spend:.2f}/${budget:.2f})"})
    elif pct_used >= 75:
        alerts.append({"level": "info", "message": f"75% of budget consumed"})
    if projected_overage > 0:
        alerts.append({"level": "warning", "message": f"Projected overage: ${projected_overage:.2f}"})
    return {
        "current_spend": current_spend,
        "budget": budget,
        "pct_used": pct_used,
        "projected_spend": projected,
        "projected_overage": projected_overage,
        "alerts": alerts,
        "status": "critical" if pct_used >= 100 else "warning" if pct_used >= 75 else "ok",
    }
