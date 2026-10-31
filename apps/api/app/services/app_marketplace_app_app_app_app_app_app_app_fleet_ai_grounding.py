"""Fleet AI Grounding Engine — track AI response grounding in source data."""
from __future__ import annotations
def fleet_ai_grounding(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    responses_24h = sum(e.get("responses_24h", 0) for e in engines)
    grounded_pct = round(sum(e.get("grounded_pct", 0) for e in engines) / max(len(engines), 1), 1)
    sources_cited = sum(e.get("sources", 0) for e in engines)
    return {"engines": len(engines), "active": len(active), "responses_24h": responses_24h,
            "grounded_pct": grounded_pct, "sources": sources_cited, "reliable": grounded_pct > 90}
