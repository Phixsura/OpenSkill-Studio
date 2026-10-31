"""Fleet DORA MTTR — classify mean time to restore."""
from __future__ import annotations
def fleet_dora_mttr(mttr_hours: float) -> dict:
    if mttr_hours <= 1:
        level = "Elite"
    elif mttr_hours <= 24:
        level = "High"
    elif mttr_hours <= 168:
        level = "Medium"
    else:
        level = "Low"
    return {"mttr_hours": mttr_hours, "level": level, "elite": level == "Elite"}
