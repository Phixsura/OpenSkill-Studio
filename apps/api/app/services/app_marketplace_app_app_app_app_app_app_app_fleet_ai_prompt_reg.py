"""Fleet AI Prompt Registry — track versioned prompt templates."""
from __future__ import annotations
def fleet_ai_prompt_registry(registries: list[dict]) -> dict:
    active = [r for r in registries if r.get("active", True)]
    templates = sum(r.get("templates", 0) for r in registries)
    versions = sum(r.get("versions", 0) for r in registries)
    return {"registries": len(registries), "active": len(active), "templates": templates,
            "versions": versions, "organized": templates > 0 and versions >= templates}
