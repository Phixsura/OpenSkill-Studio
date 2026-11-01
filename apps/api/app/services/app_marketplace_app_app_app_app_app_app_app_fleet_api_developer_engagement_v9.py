"""Fleet API Developer Engagement v9 — track developer engagement metrics."""
from __future__ import annotations
def fleet_api_developer_engagement_v9(metrics: list[dict]) -> dict:
    active_devs = sum(m.get("active_devs", 0) for m in metrics)
    api_calls_per_dev = sum(m.get("calls_per_dev", 0) for m in metrics) / len(metrics) if metrics else 0
    nps_score = sum(m.get("nps", 0) for m in metrics) / len(metrics) if metrics else 0
    return {"metrics": len(metrics), "active_developers": active_devs,
            "avg_calls_per_dev": round(api_calls_per_dev, 1), "nps_score": round(nps_score, 1),
            "healthy": nps_score > 50}
