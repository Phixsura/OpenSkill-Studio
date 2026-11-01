"""Fleet API Integration v9 — track third-party API integration health."""
from __future__ import annotations
def fleet_api_integration_v9(integrations: list[dict]) -> dict:
    active = [i for i in integrations if i.get("active")]
    healthy_i = [i for i in integrations if i.get("healthy")]
    calls_today = sum(i.get("calls_today", 0) for i in integrations)
    return {"integrations": len(integrations), "active": len(active), "healthy": len(healthy_i),
            "calls_today": calls_today, "all_healthy": len(healthy_i) == len(integrations)}
