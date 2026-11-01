"""Fleet AI Traffic Split — track weighted traffic distribution across AI models."""
from __future__ import annotations
def fleet_ai_traffic_split(splitters: list[dict]) -> dict:
    active = [s for s in splitters if s.get("active", True)]
    splits = sum(s.get("splits", 0) for s in splitters)
    requests_24h = sum(s.get("requests_24h", 0) for s in splitters)
    variants = sum(s.get("variants", 0) for s in splitters)
    return {"splitters": len(splitters), "active": len(active), "splits": splits,
            "requests_24h": requests_24h, "variants": variants, "splitting": variants > 1}
