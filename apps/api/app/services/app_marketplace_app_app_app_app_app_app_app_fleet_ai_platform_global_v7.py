"""Fleet AI Global v7 — track worldwide AI platform deployment."""
from __future__ import annotations
def fleet_ai_global_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    regions = sum(s.get("regions", 0) for s in systems)
    countries = sum(s.get("countries", 0) for s in systems)
    languages = sum(s.get("languages", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "regions": regions,
            "countries": countries, "languages": languages, "global": countries > 50}
