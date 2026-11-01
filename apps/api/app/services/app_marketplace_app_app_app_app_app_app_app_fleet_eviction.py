"""Fleet eviction tracker — monitor pod evictions."""
from __future__ import annotations
def fleet_eviction_tracker(events: list[dict]) -> dict:
    by_reason: dict[str, int] = {}
    for e in events:
        reason = e.get("reason", "unknown")
        by_reason[reason] = by_reason.get(reason, 0) + 1
    return {"total": len(events), "by_reason": by_reason, "high_rate": len(events) > 10}
