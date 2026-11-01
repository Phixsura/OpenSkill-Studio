"""Fleet API Performance v9 — track API performance benchmarks."""
from __future__ import annotations
def fleet_api_performance_v9(endpoints: list[dict]) -> dict:
    within_sla = [e for e in endpoints if e.get("within_sla")]
    avg_response = sum(e.get("response_ms", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    throughput = sum(e.get("rps", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "within_sla": len(within_sla),
            "avg_response_ms": round(avg_response, 1), "total_rps": throughput,
            "healthy": len(within_sla) == len(endpoints)}
