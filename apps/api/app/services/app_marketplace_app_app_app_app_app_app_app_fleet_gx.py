"""Fleet Great Expectations — track data quality validation."""
from __future__ import annotations
def fleet_gx_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    expectations = sum(p.get("expectations", 0) for p in projects)
    validations_24h = sum(p.get("validations_24h", 0) for p in projects)
    success_rate = round(sum(p.get("success_rate", 100) for p in projects) / max(len(projects), 1), 1)
    return {"projects": len(projects), "active": len(active), "expectations": expectations,
            "validations_24h": validations_24h, "success_rate": success_rate}
