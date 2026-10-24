"""Service level indicator — track SLIs against objectives."""
from __future__ import annotations


def create_sli(name: str, metric: str, good_events: int, total_events: int,
               objective_pct: float = 99.9) -> dict:
    ratio = round(good_events / max(total_events, 1) * 100, 3)
    budget_total = round((100 - objective_pct) / 100 * total_events)
    bad_events = total_events - good_events
    budget_remaining = max(0, budget_total - bad_events)
    return {"name": name, "metric": metric, "good": good_events, "total": total_events,
            "ratio_pct": ratio, "objective_pct": objective_pct,
            "meeting_objective": ratio >= objective_pct,
            "error_budget_total": budget_total,
            "error_budget_remaining": budget_remaining,
            "budget_consumed_pct": round(bad_events / max(budget_total, 1) * 100, 1)}


def sli_summary(slis: list[dict]) -> dict:
    meeting = sum(1 for s in slis if s["meeting_objective"])
    avg_ratio = round(sum(s["ratio_pct"] for s in slis) / max(len(slis), 1), 3)
    critical = [s["name"] for s in slis if s["budget_consumed_pct"] > 80]
    return {"total": len(slis), "meeting": meeting, "failing": len(slis) - meeting,
            "avg_ratio": avg_ratio, "critical_slis": critical,
            "all_meeting": meeting == len(slis)}
