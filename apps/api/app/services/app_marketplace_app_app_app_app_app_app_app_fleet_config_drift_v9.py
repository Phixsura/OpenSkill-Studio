"""Fleet Config Drift v9 — detect configuration drift across environments."""
from __future__ import annotations
def fleet_config_drift_v9(configs: list[dict]) -> dict:
    drifted = [c for c in configs if c.get("drifted")]
    synced = [c for c in configs if not c.get("drifted")]
    return {"total": len(configs), "synced": len(synced), "drifted": len(drifted),
            "drift_pct": round(len(drifted) / len(configs) * 100, 1) if configs else 0,
            "healthy": len(drifted) == 0}
