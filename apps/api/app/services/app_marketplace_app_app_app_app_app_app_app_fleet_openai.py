"""Fleet OpenAI — track GPT API integration."""
from __future__ import annotations
def fleet_openai_status(orgs: list[dict]) -> dict:
    active = [o for o in orgs if o.get("active", True)]
    requests_24h = sum(o.get("requests_24h", 0) for o in orgs)
    cost_24h = sum(o.get("cost_usd_24h", 0) for o in orgs)
    return {"orgs": len(orgs), "active": len(active), "requests_24h": requests_24h,
            "cost_24h": round(cost_24h, 2), "all_active": len(active) == len(orgs)}
