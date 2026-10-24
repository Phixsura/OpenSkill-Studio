"""Error budget tracker — track SLO error budget consumption."""
from __future__ import annotations


def calculate_budget(slo_target: float, total_requests: int, failed_requests: int,
                     period_days: int = 30) -> dict:
    budget_total = round((1 - slo_target) * total_requests)
    budget_consumed = failed_requests
    budget_remaining = max(0, budget_total - budget_consumed)
    pct_consumed = round(budget_consumed / max(budget_total, 1) * 100, 1)
    days_remaining = period_days - (period_days * pct_consumed / 100)
    status = "ok" if pct_consumed < 80 else ("warning" if pct_consumed < 100 else "exhausted")
    return {"slo_target": slo_target, "budget_total": budget_total,
            "budget_consumed": budget_consumed, "budget_remaining": budget_remaining,
            "pct_consumed": pct_consumed, "status": status,
            "projected_days_left": round(max(0, days_remaining), 1)}


def budget_trend(snapshots: list[dict]) -> dict:
    if len(snapshots) < 2:
        return {"trend": "insufficient_data", "snapshots": len(snapshots)}
    deltas = [snapshots[i]["pct_consumed"] - snapshots[i-1]["pct_consumed"]
              for i in range(1, len(snapshots))]
    avg_delta = round(sum(deltas) / len(deltas), 2)
    trend = "improving" if avg_delta < 0 else ("stable" if avg_delta < 1 else "worsening")
    return {"trend": trend, "avg_daily_change": avg_delta, "snapshots": len(snapshots)}
