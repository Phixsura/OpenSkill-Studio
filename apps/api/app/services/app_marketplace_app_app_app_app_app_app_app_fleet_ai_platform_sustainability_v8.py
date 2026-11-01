"""Fleet AI Sustainability v8 — track ultimate AI environmental impact."""
from __future__ import annotations
def fleet_ai_sustainability_v8(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    carbon = round(sum(t.get("carbon_kg", 0) for t in trackers), 1)
    renewable = round(sum(t.get("renewable_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    pue = round(sum(t.get("pue", 0) for t in trackers) / max(len(trackers), 1), 2)
    return {"trackers": len(trackers), "active": len(active), "carbon": carbon,
            "renewable": renewable, "pue": pue, "green": renewable > 95}
