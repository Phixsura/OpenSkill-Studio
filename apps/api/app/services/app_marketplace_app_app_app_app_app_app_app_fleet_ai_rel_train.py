"""Fleet AI Release Train — track coordinated multi-service AI releases."""
from __future__ import annotations
def fleet_ai_release_train(trains: list[dict]) -> dict:
    active = [t for t in trains if t.get("active", True)]
    services = sum(t.get("services", 0) for t in trains)
    releases_24h = sum(t.get("releases_24h", 0) for t in trains)
    on_time_pct = round(sum(t.get("on_time_pct", 0) for t in trains) / max(len(trains), 1), 1)
    return {"trains": len(trains), "active": len(active), "services": services,
            "releases_24h": releases_24h, "on_time_pct": on_time_pct, "punctual": on_time_pct > 90}
