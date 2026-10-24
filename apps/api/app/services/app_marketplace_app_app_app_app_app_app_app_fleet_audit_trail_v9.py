"""Fleet Audit Trail v9 — track compliance audit events and retention."""
from __future__ import annotations
def fleet_audit_trail_v9(events: list[dict]) -> dict:
    critical = [e for e in events if e.get("severity") == "critical"]
    retained = [e for e in events if e.get("retained")]
    return {"total_events": len(events), "critical": len(critical), "retained": len(retained),
            "retention_pct": round(len(retained) / len(events) * 100, 1) if events else 0,
            "healthy": len(retained) == len(events)}
