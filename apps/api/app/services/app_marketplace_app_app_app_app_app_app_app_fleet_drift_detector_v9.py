"""Fleet Drift Detector v9 — detect runtime drift from declared state."""
from __future__ import annotations
def fleet_drift_detector_v9(resources: list[dict]) -> dict:
    drifted = [r for r in resources if r.get("drifted")]
    auto_fixed = [r for r in resources if r.get("auto_remediated")]
    severity_high = [r for r in resources if r.get("drift_severity") == "high"]
    return {"resources": len(resources), "drifted": len(drifted), "auto_fixed": len(auto_fixed),
            "high_severity": len(severity_high), "healthy": len(drifted) == 0}
