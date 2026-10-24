"""Fleet AI Structured Output — track JSON/schema-constrained generation."""
from __future__ import annotations
def fleet_ai_structured(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    generations_24h = sum(s.get("generations_24h", 0) for s in services)
    validation_rate = round(sum(s.get("valid_pct", 100) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "active": len(active), "generations_24h": generations_24h,
            "validation_rate": validation_rate, "reliable": validation_rate >= 99}
