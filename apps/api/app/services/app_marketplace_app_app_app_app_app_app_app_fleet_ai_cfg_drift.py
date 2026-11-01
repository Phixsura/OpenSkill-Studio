"""Fleet AI Config Drift Detector — track AI config deviation from desired state."""
from __future__ import annotations
def fleet_ai_config_drift(detectors: list[dict]) -> dict:
    active = [d for d in detectors if d.get("active", True)]
    resources_monitored = sum(d.get("resources", 0) for d in detectors)
    drifts_24h = sum(d.get("drifts_24h", 0) for d in detectors)
    auto_remediated = sum(d.get("remediated", 0) for d in detectors)
    return {"detectors": len(detectors), "active": len(active), "resources": resources_monitored,
            "drifts_24h": drifts_24h, "remediated": auto_remediated, "clean": drifts_24h == auto_remediated}
