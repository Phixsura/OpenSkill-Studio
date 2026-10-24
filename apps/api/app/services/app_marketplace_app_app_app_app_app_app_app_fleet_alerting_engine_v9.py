"""Fleet Alerting Engine v9 — track alert rules, firing, and silencing."""
from __future__ import annotations
def fleet_alerting_engine_v9(alerts: list[dict]) -> dict:
    firing = [a for a in alerts if a.get("state") == "firing"]
    silenced = [a for a in alerts if a.get("state") == "silenced"]
    resolved = [a for a in alerts if a.get("state") == "resolved"]
    return {"total": len(alerts), "firing": len(firing), "silenced": len(silenced),
            "resolved": len(resolved), "healthy": len(firing) == 0}
