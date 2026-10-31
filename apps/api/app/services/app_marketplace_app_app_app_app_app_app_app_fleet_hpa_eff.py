"""Fleet HPA effectiveness — measure autoscaler responsiveness."""
from __future__ import annotations
def fleet_hpa_effectiveness(hpas: list[dict]) -> dict:
    responsive = [h for h in hpas if h.get("scale_time_sec", 999) < 120]
    avg_time = round(sum(h.get("scale_time_sec", 0) for h in hpas) / max(len(hpas), 1), 1)
    return {"total": len(hpas), "responsive": len(responsive),
            "avg_scale_time_sec": avg_time, "effective": len(responsive) == len(hpas)}
