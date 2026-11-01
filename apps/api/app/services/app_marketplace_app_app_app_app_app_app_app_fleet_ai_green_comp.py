"""Fleet AI Green Computing — track AI carbon footprint and sustainability."""
from __future__ import annotations
def fleet_ai_green_computing(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    co2_kg_24h = round(sum(t.get("co2_kg", 0) for t in trackers), 1)
    kwh_24h = round(sum(t.get("kwh", 0) for t in trackers), 1)
    renewable_pct = round(sum(t.get("renewable_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "co2_kg_24h": co2_kg_24h,
            "kwh_24h": kwh_24h, "renewable_pct": renewable_pct, "green": renewable_pct > 80}
