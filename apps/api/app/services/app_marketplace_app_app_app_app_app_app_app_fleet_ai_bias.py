"""Fleet AI Bias Detection — track fairness and bias monitoring."""
from __future__ import annotations
def fleet_ai_bias(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active", True)]
    models_audited = sum(m.get("models_audited", 0) for m in monitors)
    bias_alerts = sum(m.get("bias_alerts_24h", 0) for m in monitors)
    return {"monitors": len(monitors), "active": len(active), "models_audited": models_audited,
            "bias_alerts": bias_alerts, "fair": bias_alerts == 0}
