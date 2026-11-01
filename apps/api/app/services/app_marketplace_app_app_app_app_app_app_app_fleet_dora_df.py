"""Fleet DORA deployment frequency — classify deployment frequency."""
from __future__ import annotations
def fleet_dora_deploy_freq(deploys_per_day: float) -> dict:
    if deploys_per_day >= 1:
        level = "Elite"
    elif deploys_per_day >= 1/7:
        level = "High"
    elif deploys_per_day >= 1/30:
        level = "Medium"
    else:
        level = "Low"
    return {"deploys_per_day": deploys_per_day, "level": level, "elite": level == "Elite"}
