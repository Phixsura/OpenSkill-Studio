"""SRE toolkit — site reliability engineering tools and metrics."""
from __future__ import annotations


def calculate_error_budget_burn(slo: float, window_days: int,
                                  elapsed_days: int, current_errors: int,
                                  total_requests: int) -> dict:
    budget_total = round(total_requests * (100 - slo) / 100)
    consumed = current_errors
    consumed_pct = round(consumed / max(budget_total, 1) * 100, 1)
    expected_pct = round(elapsed_days / max(window_days, 1) * 100, 1)
    burn_rate = round(consumed_pct / max(expected_pct, 0.1), 2)
    alert = "page" if burn_rate > 10 else "ticket" if burn_rate > 2 else "none"
    return {"budget_total": budget_total, "consumed": consumed,
            "consumed_pct": consumed_pct, "expected_pct": expected_pct,
            "burn_rate": burn_rate, "alert": alert,
            "healthy": burn_rate <= 1}


def toil_budget(team_hours: float, toil_hours: float) -> dict:
    toil_pct = round(toil_hours / max(team_hours, 1) * 100, 1)
    target = 50  # SRE book recommends < 50% toil
    return {"team_hours": team_hours, "toil_hours": toil_hours,
            "toil_pct": toil_pct, "target_pct": target,
            "within_budget": toil_pct <= target,
            "automation_opportunity": round(max(0, toil_hours - team_hours * target / 100), 1)}
