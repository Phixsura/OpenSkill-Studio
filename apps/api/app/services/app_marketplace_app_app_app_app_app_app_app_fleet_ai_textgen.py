"""Fleet AI Text Generation — track content generation."""
from __future__ import annotations
def fleet_ai_textgen(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    generations_24h = sum(s.get("generations_24h", 0) for s in services)
    tokens_generated = sum(s.get("tokens_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "generations_24h": generations_24h,
            "tokens_24h": tokens_generated, "all_active": len(active) == len(services)}
