"""Error recovery — automated error recovery strategies."""

import html
from datetime import datetime, timezone

STRATEGIES = {
    "retry": {"description": "Retry the operation", "icon": "🔄", "auto": True},
    "fallback": {"description": "Use fallback value", "icon": "🔀", "auto": True},
    "skip": {"description": "Skip and continue", "icon": "⏭️", "auto": True},
    "manual": {"description": "Require manual intervention", "icon": "🛑", "auto": False},
    "circuit_break": {"description": "Open circuit breaker", "icon": "⚡", "auto": True},
}


def select_strategy(*, error_type: str, retry_count: int = 0, max_retries: int = 3) -> dict:
    if retry_count < max_retries:
        strategy = "retry"
    elif error_type in ("timeout", "connection_error"):
        strategy = "circuit_break"
    elif error_type == "validation_error":
        strategy = "skip"
    elif error_type == "not_found":
        strategy = "fallback"
    else:
        strategy = "manual"
    info = STRATEGIES[strategy]
    return {"strategy": strategy, "description": info["description"],
            "icon": info["icon"], "auto_recoverable": info["auto"],
            "retry_count": retry_count, "max_retries": max_retries}


def build_recovery_report(*, errors: list[dict]) -> dict:
    recovered = sum(1 for e in errors if e.get("recovered"))
    strategies_used: dict[str, int] = {}
    for e in errors:
        s = e.get("strategy", "manual")
        strategies_used[s] = strategies_used.get(s, 0) + 1
    return {"total_errors": len(errors), "recovered": recovered,
            "unrecovered": len(errors) - recovered,
            "recovery_rate": round(recovered / max(len(errors), 1) * 100, 1),
            "strategies_used": strategies_used}
