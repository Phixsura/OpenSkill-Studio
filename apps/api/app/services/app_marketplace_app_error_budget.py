"""Error budget — track SLO-based error budgets for apps."""


def calculate_error_budget(*, slo_target: float, total_requests: int,
                             failed_requests: int, period_days: int = 30) -> dict:
    if slo_target <= 0 or slo_target > 100:
        return {"error": "SLO target must be between 0 and 100"}
    if total_requests == 0:
        return {"error": "No requests in period"}
    actual_success = round((total_requests - failed_requests) / total_requests * 100, 4)
    budget_total = round((100 - slo_target) / 100 * total_requests)
    budget_consumed = failed_requests
    budget_remaining = max(budget_total - budget_consumed, 0)
    budget_pct_used = round(budget_consumed / max(budget_total, 1) * 100, 1)
    daily_burn = round(budget_consumed / max(period_days, 1), 1)
    days_remaining = round(budget_remaining / max(daily_burn, 0.01), 1) if daily_burn > 0 else float("inf")
    return {
        "slo_target": slo_target,
        "actual_success_rate": actual_success,
        "meeting_slo": actual_success >= slo_target,
        "budget_total": budget_total,
        "budget_consumed": budget_consumed,
        "budget_remaining": budget_remaining,
        "budget_pct_used": budget_pct_used,
        "daily_burn_rate": daily_burn,
        "estimated_days_remaining": min(days_remaining, 999),
        "status": "ok" if budget_pct_used < 80 else "warning" if budget_pct_used < 100 else "exhausted",
    }
