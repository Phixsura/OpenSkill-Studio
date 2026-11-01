"""Fleet Datadog — track Datadog monitoring integration."""
from __future__ import annotations
def fleet_datadog_status(integrations: list[dict]) -> dict:
    active = [i for i in integrations if i.get("active", True)]
    monitors = sum(i.get("monitors", 0) for i in integrations)
    alerts_firing = sum(i.get("alerts_firing", 0) for i in integrations)
    return {"total": len(integrations), "active": len(active), "monitors": monitors,
            "alerts_firing": alerts_firing, "calm": alerts_firing == 0}
