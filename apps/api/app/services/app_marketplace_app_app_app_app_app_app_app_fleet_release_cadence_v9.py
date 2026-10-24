"""Fleet Release Cadence v9 — track release rhythm and predictability."""
from __future__ import annotations
def fleet_release_cadence_v9(teams: list[dict]) -> dict:
    on_cadence = [t for t in teams if t.get("on_cadence")]
    releases_week = sum(t.get("releases_per_week", 0) for t in teams)
    avg_interval = sum(t.get("avg_interval_hours", 0) for t in teams) / len(teams) if teams else 0
    return {"teams": len(teams), "on_cadence": len(on_cadence), "releases_per_week": releases_week,
            "avg_interval_hours": round(avg_interval, 1), "healthy": len(on_cadence) == len(teams)}
