"""Fleet Service Reliability v9 — track overall service reliability score."""
from __future__ import annotations
def fleet_service_reliability_v9(services: list[dict]) -> dict:
    scores = [s.get("reliability_score", 0) for s in services]
    avg = sum(scores) / len(scores) if scores else 0
    nines = "99.99%" if avg > 99 else "99.9%" if avg > 95 else "99%"
    return {"services": len(services), "avg_reliability": round(avg, 2), "uptime_class": nines,
            "healthy": avg > 99}
