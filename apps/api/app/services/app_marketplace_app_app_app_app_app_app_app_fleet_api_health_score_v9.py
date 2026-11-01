"""Fleet API Health Score v9 — aggregate API health across all endpoints."""
from __future__ import annotations
def fleet_api_health_score_v9(endpoints: list[dict]) -> dict:
    scores = [e.get("health_score", 0) for e in endpoints]
    avg = sum(scores) / len(scores) if scores else 0
    critical = [e for e in endpoints if e.get("health_score", 100) < 50]
    degraded = [e for e in endpoints if 50 <= e.get("health_score", 100) < 80]
    return {"endpoints": len(endpoints), "avg_health_score": round(avg, 1),
            "critical": len(critical), "degraded": len(degraded),
            "healthy": len(critical) == 0 and len(degraded) == 0}
