"""Error budget tracker — SRE error budget consumption and burn rate."""
from __future__ import annotations


def calculate_error_budget(*, slo_target: float = 99.9, period_hours: int = 720,
                            total_requests: int = 0, failed_requests: int = 0,
                            elapsed_hours: int = 0) -> dict:
    budget_pct = 100 - slo_target  # e.g. 0.1% for 99.9% SLO
    budget_requests = int(total_requests * budget_pct / 100)
    consumed_pct = round(failed_requests / max(budget_requests, 1) * 100, 1)
    remaining_pct = max(0, round(100 - consumed_pct, 1))
    elapsed_pct = round(elapsed_hours / max(period_hours, 1) * 100, 1)
    burn_rate = round(consumed_pct / max(elapsed_pct, 0.1), 2) if elapsed_pct > 0 else 0
    status = "exhausted" if remaining_pct <= 0 else "critical" if burn_rate > 2 else \
             "warning" if burn_rate > 1 else "healthy"
    return {
        "slo_target": slo_target, "slo_display": f"{slo_target}%",
        "budget_total": budget_requests, "budget_consumed": failed_requests,
        "consumed_pct": consumed_pct, "remaining_pct": remaining_pct,
        "burn_rate": burn_rate,
        "burn_rate_display": f"{burn_rate}x",
        "elapsed_pct": elapsed_pct,
        "status": status,
        "period_hours": period_hours,
    }
