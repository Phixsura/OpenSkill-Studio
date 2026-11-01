"""Fleet error taxonomy — categorize errors by root cause."""
from __future__ import annotations
def fleet_error_taxonomy(errors: list[dict]) -> dict:
    by_cause: dict[str, int] = {}
    for e in errors:
        cause = e.get("root_cause", "unknown")
        by_cause[cause] = by_cause.get(cause, 0) + 1
    top = max(by_cause, key=lambda k: by_cause[k]) if by_cause else None
    return {"total": len(errors), "causes": len(by_cause), "top_cause": top,
            "by_cause": by_cause}
