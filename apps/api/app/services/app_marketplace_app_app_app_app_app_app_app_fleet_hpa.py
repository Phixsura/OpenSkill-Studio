"""Fleet HPA status — track horizontal pod autoscaler state."""
from __future__ import annotations
def fleet_hpa_status(hpas: list[dict]) -> dict:
    at_max = [h for h in hpas if h.get("current", 0) >= h.get("max", 999)]
    at_min = [h for h in hpas if h.get("current", 0) <= h.get("min", 0)]
    return {"total": len(hpas), "at_max": len(at_max), "at_min": len(at_min),
            "scaling_pressure": len(at_max) > 0}
