"""Fleet environment parity — compare staging vs production configs."""
from __future__ import annotations
def fleet_env_parity(services: list[dict]) -> dict:
    matching = [s for s in services if s.get("config_matches_prod", True)]
    drifted = len(services) - len(matching)
    return {"total": len(services), "matching": len(matching), "drifted": drifted,
            "parity": drifted == 0}
