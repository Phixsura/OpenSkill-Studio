"""SLI calculator — compute Service Level Indicators from raw metrics."""
from __future__ import annotations


def compute_sli(*, metric: str, good_events: int, total_events: int,
                 slo_target: float = 99.9, period: str = "28d") -> dict:
    if total_events == 0:
        return {"metric": metric, "sli": 0, "error": "No events"}
    sli = round(good_events / total_events * 100, 3)
    met = sli >= slo_target
    budget_total = (100 - slo_target) / 100 * total_events
    budget_consumed = total_events - good_events
    budget_remaining = max(0, budget_total - budget_consumed)
    budget_pct = round(budget_consumed / max(budget_total, 1) * 100, 1)
    return {
        "metric": metric, "sli": sli, "sli_display": f"{sli}%",
        "slo_target": slo_target, "met": met,
        "good_events": good_events, "bad_events": total_events - good_events,
        "total_events": total_events, "period": period,
        "error_budget_total": round(budget_total), "error_budget_consumed": budget_consumed,
        "error_budget_remaining": round(budget_remaining),
        "error_budget_pct": budget_pct,
        "status": "met" if met else "breached",
    }


def compute_composite_sli(slis: list[dict]) -> dict:
    if not slis:
        return {"composite_sli": 0, "count": 0}
    avg = round(sum(s["sli"] for s in slis) / len(slis), 3)
    all_met = all(s["met"] for s in slis)
    breached = [s["metric"] for s in slis if not s["met"]]
    return {"composite_sli": avg, "composite_display": f"{avg}%",
            "all_met": all_met, "breached_metrics": breached, "count": len(slis)}
