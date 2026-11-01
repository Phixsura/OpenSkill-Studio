"""Fleet API Discovery v9 — track automatic API endpoint discovery."""
from __future__ import annotations
def fleet_api_discovery_v9(sources: list[dict]) -> dict:
    discovered = sum(s.get("endpoints_found", 0) for s in sources)
    registered = sum(s.get("registered", 0) for s in sources)
    stale = sum(s.get("stale", 0) for s in sources)
    return {"sources": len(sources), "discovered": discovered, "registered": registered,
            "stale": stale, "healthy": stale == 0}
