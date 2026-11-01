"""Error recovery manager — automate error recovery strategies."""
from __future__ import annotations

STRATEGIES = {
    "retry": {"description": "Retry the failed operation", "auto": True},
    "fallback": {"description": "Switch to fallback service", "auto": True},
    "circuit_break": {"description": "Open circuit breaker", "auto": True},
    "alert": {"description": "Alert on-call engineer", "auto": False},
    "rollback": {"description": "Rollback to previous version", "auto": False},
}


def select_strategy(error_type: str, consecutive_failures: int, has_fallback: bool) -> dict:
    if consecutive_failures <= 2:
        strategy = "retry"
    elif has_fallback and consecutive_failures <= 5:
        strategy = "fallback"
    elif consecutive_failures <= 10:
        strategy = "circuit_break"
    else:
        strategy = "rollback"
    info = STRATEGIES.get(strategy, STRATEGIES["alert"])
    return {"strategy": strategy, **info, "error_type": error_type,
            "consecutive_failures": consecutive_failures}


def recovery_report(events: list[dict]) -> dict:
    by_strategy: dict[str, int] = {}
    auto_recovered = 0
    for e in events:
        s = e.get("strategy", "unknown")
        by_strategy[s] = by_strategy.get(s, 0) + 1
        if STRATEGIES.get(s, {}).get("auto", False):
            auto_recovered += 1
    return {"total_events": len(events), "by_strategy": by_strategy,
            "auto_recovered": auto_recovered,
            "auto_pct": round(auto_recovered / max(len(events), 1) * 100)}
