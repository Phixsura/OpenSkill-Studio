"""Fleet endpoint SLA — track per-endpoint SLA compliance."""
from __future__ import annotations
def fleet_endpoint_sla(endpoints: list[dict]) -> dict:
    meeting = [e for e in endpoints if e.get("p99_ms", 0) <= e.get("sla_ms", 500)]
    violating = len(endpoints) - len(meeting)
    return {"total": len(endpoints), "meeting_sla": len(meeting),
            "violating": violating, "compliance_pct": round(len(meeting) / max(len(endpoints), 1) * 100, 1)}
