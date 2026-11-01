"""Fleet AI System Prompt Manager — track system prompt versioning."""
from __future__ import annotations
def fleet_ai_system_prompt(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    prompts = sum(m.get("prompts", 0) for m in managers)
    versions = sum(m.get("versions", 0) for m in managers)
    uses_24h = sum(m.get("uses_24h", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "prompts": prompts,
            "versions": versions, "uses_24h": uses_24h, "managed": prompts > 0}
