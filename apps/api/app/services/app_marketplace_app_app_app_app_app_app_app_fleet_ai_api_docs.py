"""Fleet AI API Docs Generator — track automated API documentation."""
from __future__ import annotations
def fleet_ai_api_docs(generators: list[dict]) -> dict:
    active = [g for g in generators if g.get("active", True)]
    endpoints_documented = sum(g.get("endpoints", 0) for g in generators)
    examples = sum(g.get("examples", 0) for g in generators)
    views_24h = sum(g.get("views_24h", 0) for g in generators)
    return {"generators": len(generators), "active": len(active), "endpoints": endpoints_documented,
            "examples": examples, "views_24h": views_24h, "comprehensive": examples > endpoints_documented}
