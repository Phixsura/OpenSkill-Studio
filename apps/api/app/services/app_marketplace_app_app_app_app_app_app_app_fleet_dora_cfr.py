"""Fleet DORA change failure rate — classify CFR performance."""
from __future__ import annotations
def fleet_dora_cfr(cfr_pct: float) -> dict:
    if cfr_pct <= 5:
        level = "Elite"
    elif cfr_pct <= 10:
        level = "High"
    elif cfr_pct <= 30:
        level = "Medium"
    else:
        level = "Low"
    return {"cfr_pct": cfr_pct, "level": level, "elite": level == "Elite"}
