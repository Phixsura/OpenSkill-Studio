"""Fleet audit log — aggregate audit event stats."""
from __future__ import annotations
def fleet_audit_log_stats(events: list[dict]) -> dict:
    by_type: dict[str, int] = {}
    for e in events:
        t = e.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    return {"total_events": len(events), "by_type": by_type, "types": len(by_type)}
