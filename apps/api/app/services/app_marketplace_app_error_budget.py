"""Error budget — SLO-based error budget tracking for reliability."""


def compute_error_budget(*, slo_target: float, total_requests: int, failed_requests: int) -> dict:
    allowed_failures = int(total_requests * (1 - slo_target / 100))
    budget_remaining = allowed_failures - failed_requests
    budget_pct = round(budget_remaining / max(allowed_failures, 1) * 100, 1)
    return {
        "slo_target": slo_target, "total_requests": total_requests,
        "failed_requests": failed_requests, "allowed_failures": allowed_failures,
        "budget_remaining": max(0, budget_remaining),
        "budget_pct": max(0, budget_pct), "budget_exhausted": budget_remaining <= 0,
    }


def get_burn_rate(*, budget_remaining_pct: float, elapsed_pct: float) -> dict:
    if elapsed_pct == 0:
        return {"burn_rate": 0, "on_track": True}
    expected_remaining = 100 - elapsed_pct
    burn_rate = round((100 - budget_remaining_pct) / elapsed_pct, 2)
    on_track = budget_remaining_pct >= expected_remaining * 0.8
    return {"burn_rate": burn_rate, "on_track": on_track,
            "alert": "critical" if burn_rate > 2 else "warning" if burn_rate > 1.5 else None}


def recommend_action(*, budget_pct: float, burn_rate: float) -> str:
    if budget_pct <= 0:
        return "FREEZE: Error budget exhausted. No deployments until budget recovers."
    if burn_rate > 2:
        return "ALERT: Burning budget 2x faster than expected. Investigate immediately."
    if burn_rate > 1.5:
        return "CAUTION: Budget consumption elevated. Review recent changes."
    return "OK: Error budget healthy. Safe to deploy."
