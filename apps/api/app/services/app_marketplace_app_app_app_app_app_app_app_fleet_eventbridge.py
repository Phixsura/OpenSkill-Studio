"""Fleet EventBridge — track event bus health."""
from __future__ import annotations
def fleet_eventbridge_status(buses: list[dict]) -> dict:
    total_events = sum(b.get("events_24h", 0) for b in buses)
    rules = sum(b.get("rules", 0) for b in buses)
    failed_invocations = sum(b.get("failed_invocations", 0) for b in buses)
    return {"buses": len(buses), "events_24h": total_events, "rules": rules,
            "failed_invocations": failed_invocations, "healthy": failed_invocations == 0}
