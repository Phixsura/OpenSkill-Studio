"""Fleet config drift — detect configuration divergence across instances."""
from __future__ import annotations
def detect_config_drift(instances: list[dict]) -> dict:
    if not instances:
        return {"drifted": 0, "total": 0, "consistent": True}
    baseline = instances[0].get("config_hash", "")
    drifted = [i for i in instances if i.get("config_hash", "") != baseline]
    return {"drifted": len(drifted), "total": len(instances),
            "consistent": len(drifted) == 0}
