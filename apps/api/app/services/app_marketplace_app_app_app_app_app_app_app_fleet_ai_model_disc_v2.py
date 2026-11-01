"""Fleet AI Model Discovery v2 — track intelligent model search and recommendation."""
from __future__ import annotations
def fleet_ai_model_discovery_v2(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    searches_24h = sum(e.get("searches_24h", 0) for e in engines)
    models_indexed = sum(e.get("models", 0) for e in engines)
    recommendations = sum(e.get("recommendations", 0) for e in engines)
    return {"engines": len(engines), "active": len(active), "searches_24h": searches_24h,
            "models": models_indexed, "recommendations": recommendations, "intelligent": recommendations > 0}
