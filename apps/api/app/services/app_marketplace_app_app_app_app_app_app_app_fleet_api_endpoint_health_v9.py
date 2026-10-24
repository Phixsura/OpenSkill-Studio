"""Fleet API Endpoint Health v9 — track per-endpoint health scores."""
from __future__ import annotations
def fleet_api_endpoint_health_v9(endpoints: list[dict]) -> dict:
    healthy_e = [e for e in endpoints if e.get("health_score", 0) > 90]
    degraded = [e for e in endpoints if 50 < e.get("health_score", 0) <= 90]
    critical = [e for e in endpoints if e.get("health_score", 0) <= 50]
    avg_score = sum(e.get("health_score", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    return {"endpoints": len(endpoints), "healthy": len(healthy_e), "degraded": len(degraded),
            "critical": len(critical), "avg_score": round(avg_score, 1), "all_healthy": len(critical) == 0}
