"""Fleet AI Playground — track interactive AI experimentation."""
from __future__ import annotations
def fleet_ai_playground(instances: list[dict]) -> dict:
    active = [i for i in instances if i.get("active", True)]
    sessions_24h = sum(i.get("sessions_24h", 0) for i in instances)
    prompts_24h = sum(i.get("prompts_24h", 0) for i in instances)
    return {"instances": len(instances), "active": len(active), "sessions_24h": sessions_24h,
            "prompts_24h": prompts_24h, "popular": sessions_24h > 1000}
