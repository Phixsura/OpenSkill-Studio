"""Error budget tracker — track SLO error budget consumption per app."""
from __future__ import annotations


def track_error_budget(*, app_id: str, slo_target: float = 99.9,
                         total_requests: int, failed_requests: int,
                         period_days: int = 30, elapsed_days: int = 15) -> dict:
    budget_pct = 100 - slo_target
    budget_total = int(total_requests * budget_pct / 100)
    consumed_pct = round(failed_requests / max(budget_total, 1) * 100, 1)
    remaining_pct = max(0, round(100 - consumed_pct, 1))
    elapsed_pct = round(elapsed_days / max(period_days, 1) * 100, 1)
    burn_rate = round(consumed_pct / max(elapsed_pct, 0.1), 2)
    status = "exhausted" if remaining_pct <= 0 else "critical" if burn_rate > 2 else \
             "warning" if burn_rate > 1 else "healthy"
    return {
        "app_id": app_id, "slo_target": slo_target,
        "budget_total": budget_total, "budget_consumed": failed_requests,
        "consumed_pct": consumed_pct, "remaining_pct": remaining_pct,
        "burn_rate": burn_rate, "status": status,
        "days_remaining": period_days - elapsed_days,
    }
