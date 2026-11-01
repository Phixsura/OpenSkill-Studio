"""Fleet Together AI — track open-source model hosting."""
from __future__ import annotations
def fleet_together_status(models: list[dict]) -> dict:
    deployed = [m for m in models if m.get("deployed", True)]
    inferences_24h = sum(m.get("inferences_24h", 0) for m in models)
    gpu_hours = sum(m.get("gpu_hours_24h", 0) for m in models)
    return {"models": len(models), "deployed": len(deployed), "inferences_24h": inferences_24h,
            "gpu_hours_24h": round(gpu_hours, 1), "all_deployed": len(deployed) == len(models)}
