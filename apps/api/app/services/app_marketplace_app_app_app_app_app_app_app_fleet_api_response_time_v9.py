"""Fleet API Response Time v9 — track response time SLA compliance."""
from __future__ import annotations
def fleet_api_response_time_v9(endpoints: list[dict]) -> dict:
    within_sla = [e for e in endpoints if e.get("within_sla")]
    avg_ms = sum(e.get("avg_ms", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    p99_max = max((e.get("p99_ms", 0) for e in endpoints), default=0)
    return {"endpoints": len(endpoints), "within_sla": len(within_sla), "avg_ms": round(avg_ms, 1),
            "max_p99_ms": p99_max, "healthy": len(within_sla) == len(endpoints)}
