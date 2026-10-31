"""Fleet API Reliability Score v9 — comprehensive reliability metric."""
from __future__ import annotations
def fleet_api_reliability_score_v9(services: list[dict]) -> dict:
    scores = [s.get("reliability_score", 0) for s in services]
    avg = sum(scores) / len(scores) if scores else 0
    above_99 = [s for s in services if s.get("reliability_score", 0) > 99]
    incidents_30d = sum(s.get("incidents_30d", 0) for s in services)
    return {"services": len(services), "avg_reliability": round(avg, 2), "above_99_pct": len(above_99),
            "incidents_30d": incidents_30d, "healthy": avg > 99}
