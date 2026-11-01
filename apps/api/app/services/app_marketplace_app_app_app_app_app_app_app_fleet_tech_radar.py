"""Fleet tech radar — track technology adoption lifecycle."""
from __future__ import annotations
def fleet_tech_radar(technologies: list[dict]) -> dict:
    adopt = [t for t in technologies if t.get("ring") == "adopt"]
    trial = [t for t in technologies if t.get("ring") == "trial"]
    assess = [t for t in technologies if t.get("ring") == "assess"]
    hold = [t for t in technologies if t.get("ring") == "hold"]
    return {"total": len(technologies), "adopt": len(adopt), "trial": len(trial),
            "assess": len(assess), "hold": len(hold)}
