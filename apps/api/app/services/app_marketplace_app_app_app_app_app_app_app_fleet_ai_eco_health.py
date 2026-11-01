"""Fleet AI Ecosystem Health — track overall AI ecosystem vitality."""
from __future__ import annotations
def fleet_ai_ecosystem_health(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active", True)]
    plugins = sum(m.get("plugins", 0) for m in monitors)
    integrations = sum(m.get("integrations", 0) for m in monitors)
    community_size = sum(m.get("community", 0) for m in monitors)
    growth_pct = round(sum(m.get("growth_pct", 0) for m in monitors) / max(len(monitors), 1), 1)
    return {"monitors": len(monitors), "active": len(active), "plugins": plugins,
            "integrations": integrations, "community": community_size, "growth_pct": growth_pct, "thriving": growth_pct > 10}
