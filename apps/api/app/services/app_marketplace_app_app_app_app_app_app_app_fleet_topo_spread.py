"""Fleet topology spread — check zone/region distribution."""
from __future__ import annotations
def fleet_topology_spread(deployments: list[dict]) -> dict:
    well_spread = [d for d in deployments if d.get("zones", 1) >= 3]
    single_zone = [d for d in deployments if d.get("zones", 1) == 1]
    return {"total": len(deployments), "well_spread": len(well_spread),
            "single_zone": len(single_zone), "resilient": len(single_zone) == 0}
