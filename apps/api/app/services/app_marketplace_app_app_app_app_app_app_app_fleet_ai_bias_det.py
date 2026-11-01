"""Fleet AI Bias Detection — track fairness and bias metrics in AI models."""
from __future__ import annotations
def fleet_ai_bias_detection(detectors: list[dict]) -> dict:
    active = [d for d in detectors if d.get("active", True)]
    scans_24h = sum(d.get("scans_24h", 0) for d in detectors)
    bias_alerts = sum(d.get("bias_alerts", 0) for d in detectors)
    fairness_score = round(sum(d.get("fairness_score", 0) for d in detectors) / max(len(detectors), 1), 2)
    return {"detectors": len(detectors), "active": len(active), "scans_24h": scans_24h,
            "bias_alerts": bias_alerts, "fairness_score": fairness_score, "fair": fairness_score > 0.9}
