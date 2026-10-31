"""Fleet API Versioning Strategy v9 — track URL vs header versioning."""
from __future__ import annotations
def fleet_api_versioning_strategy_v9(apis: list[dict]) -> dict:
    url_versioned = [a for a in apis if a.get("strategy") == "url"]
    header_versioned = [a for a in apis if a.get("strategy") == "header"]
    query_versioned = [a for a in apis if a.get("strategy") == "query"]
    return {"apis": len(apis), "url": len(url_versioned), "header": len(header_versioned),
            "query": len(query_versioned), "healthy": True}
