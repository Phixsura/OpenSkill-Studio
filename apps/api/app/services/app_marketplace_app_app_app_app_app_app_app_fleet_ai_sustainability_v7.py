"""Fleet AI Sustainability v7 — track AI platform environmental impact."""
from __future__ import annotations
def fleet_ai_sustainability_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    carbon_kg = round(sum(t.get("carbon_kg", 0) for t in trackers), 1)
    renewable_pct = round(sum(t.get("renewable_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    pue = round(sum(t.get("pue", 0) for t in trackers) / max(len(trackers), 1), 2)
    return {"trackers": len(trackers), "active": len(active), "carbon_kg": carbon_kg,
            "renewable_pct": renewable_pct, "pue": pue, "green": renewable_pct > 90}
