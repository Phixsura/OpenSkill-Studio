"""Fleet sustainability — track green computing metrics."""
from __future__ import annotations
def fleet_sustainability(metrics: dict) -> dict:
    carbon_kg = metrics.get("carbon_kg_per_month", 0)
    renewable_pct = metrics.get("renewable_energy_pct", 0)
    pue = metrics.get("pue", 1.5)
    grade = "A" if renewable_pct >= 90 and pue <= 1.2 else ("B" if renewable_pct >= 50 else "C")
    return {"carbon_kg": carbon_kg, "renewable_pct": renewable_pct, "pue": pue, "grade": grade}
