"""Fleet AI Success v7 — track platform customer success metrics."""
from __future__ import annotations
def fleet_ai_success_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    health_score = round(sum(t.get("health", 0) for t in trackers) / max(len(trackers), 1), 1)
    churn_risk = round(sum(t.get("churn_risk_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    expansion_rev = round(sum(t.get("expansion_usd", 0) for t in trackers), 2)
    return {"trackers": len(trackers), "active": len(active), "health": health_score,
            "churn_risk": churn_risk, "expansion": expansion_rev, "healthy": health_score > 80}
