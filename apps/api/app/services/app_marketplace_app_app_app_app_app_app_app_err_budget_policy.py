"""Error budget policy — enforce error budget consumption rules."""
from __future__ import annotations


def create_budget(slo_target: float, total_requests: int, window_days: int = 30) -> dict:
    allowed_errors = int(total_requests * (100 - slo_target) / 100)
    return {"slo_target": slo_target, "total_requests": total_requests,
            "allowed_errors": allowed_errors, "window_days": window_days}


def check_budget(budget: dict, actual_errors: int) -> dict:
    remaining = max(0, budget["allowed_errors"] - actual_errors)
    consumed_pct = round(actual_errors / max(budget["allowed_errors"], 1) * 100, 1)
    exhausted = actual_errors >= budget["allowed_errors"]
    action = "freeze_deploys" if exhausted else "caution" if consumed_pct > 80 else "normal"
    return {"allowed": budget["allowed_errors"], "actual": actual_errors,
            "remaining": remaining, "consumed_pct": consumed_pct,
            "exhausted": exhausted, "action": action}


def project_burn_rate(consumed_pct: float, elapsed_days: int, window_days: int) -> dict:
    daily_burn = consumed_pct / max(elapsed_days, 1)
    projected_at_end = round(daily_burn * window_days, 1)
    will_exhaust = projected_at_end > 100
    return {"daily_burn_pct": round(daily_burn, 2), "projected_at_end": projected_at_end,
            "will_exhaust": will_exhaust, "days_remaining": window_days - elapsed_days}
