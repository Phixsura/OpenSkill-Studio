"""Fleet Endpoint Discovery v9 — track API endpoint auto-discovery."""
from __future__ import annotations
def fleet_endpoint_discovery_v9(endpoints: list[dict]) -> dict:
    discovered = [e for e in endpoints if e.get("auto_discovered")]
    registered = [e for e in endpoints if e.get("registered")]
    stale = [e for e in endpoints if e.get("stale")]
    return {"endpoints": len(endpoints), "auto_discovered": len(discovered), "registered": len(registered),
            "stale": len(stale), "healthy": len(stale) == 0}
