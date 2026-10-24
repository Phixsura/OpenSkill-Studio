"""Fleet webhook analytics — track webhook event distribution."""
from __future__ import annotations
def fleet_webhook_analytics(events: list[dict]) -> dict:
    by_type: dict[str, int] = {}
    for e in events:
        t = e.get("event_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    return {"total_events": len(events), "event_types": len(by_type),
            "by_type": by_type, "diverse": len(by_type) >= 5}
