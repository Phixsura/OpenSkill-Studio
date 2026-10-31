"""Fleet Security Event v9 — track security event aggregation and alerting."""
from __future__ import annotations
def fleet_security_event_v9(events: list[dict]) -> dict:
    critical = [e for e in events if e.get("severity") == "critical"]
    high = [e for e in events if e.get("severity") == "high"]
    investigated = [e for e in events if e.get("investigated")]
    return {"total": len(events), "critical": len(critical), "high": len(high),
            "investigated": len(investigated), "healthy": len(critical) == 0}
