"""Fleet Config Drift Detector v9 — track config drift across environments."""
from __future__ import annotations
def fleet_config_drift_detector_v9(configs: list[dict]) -> dict:
    synced = [c for c in configs if c.get("synced")]
    drifted = [c for c in configs if not c.get("synced")]
    auto_fixed = [c for c in configs if c.get("auto_remediated")]
    return {"configs": len(configs), "synced": len(synced), "drifted": len(drifted),
            "auto_fixed": len(auto_fixed), "healthy": len(drifted) == 0}
