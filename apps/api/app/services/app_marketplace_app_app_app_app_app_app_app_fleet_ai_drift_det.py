"""Fleet AI Drift Detection — track data and concept drift in AI models."""
from __future__ import annotations
def fleet_ai_drift_detection(detectors: list[dict]) -> dict:
    active = [d for d in detectors if d.get("active", True)]
    alerts_24h = sum(d.get("alerts_24h", 0) for d in detectors)
    drift_score = round(sum(d.get("drift_score", 0) for d in detectors) / max(len(detectors), 1), 3)
    retrained = sum(d.get("retrained", 0) for d in detectors)
    return {"detectors": len(detectors), "active": len(active), "alerts_24h": alerts_24h,
            "drift_score": drift_score, "retrained": retrained, "stable": drift_score < 0.1}
