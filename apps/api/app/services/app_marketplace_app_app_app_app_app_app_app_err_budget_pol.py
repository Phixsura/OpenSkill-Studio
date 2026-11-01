"""Error budget policy — enforce error budget policies with actions."""
from __future__ import annotations


def evaluate_budget_policy(budget_consumed_pct: float, policies: list[dict]) -> dict:
    triggered = []
    for policy in policies:
        threshold = policy["threshold_pct"]
        if budget_consumed_pct >= threshold:
            triggered.append({"policy": policy["name"], "threshold": threshold,
                              "action": policy["action"],
                              "severity": policy.get("severity", "warning")})
    triggered.sort(key=lambda p: -p["threshold"])
    most_severe = triggered[0] if triggered else None
    return {"budget_consumed_pct": budget_consumed_pct,
            "triggered_policies": triggered,
            "recommended_action": most_severe["action"] if most_severe else "none",
            "freeze_deploys": budget_consumed_pct >= 100}


def budget_forecast(current_pct: float, daily_burn_rate: float, days_remaining: int) -> dict:
    projected = current_pct + daily_burn_rate * days_remaining
    will_exhaust = projected >= 100
    days_to_exhaust = round((100 - current_pct) / max(daily_burn_rate, 0.001))
    return {"current_pct": current_pct, "projected_pct": round(projected, 1),
            "will_exhaust": will_exhaust, "days_to_exhaustion": max(0, days_to_exhaust)}
