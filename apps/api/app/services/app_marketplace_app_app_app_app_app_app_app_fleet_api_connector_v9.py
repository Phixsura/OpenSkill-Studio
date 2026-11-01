"""Fleet API Connector v9 — track third-party API connector health."""
from __future__ import annotations
def fleet_api_connector_v9(connectors: list[dict]) -> dict:
    connected = [c for c in connectors if c.get("connected")]
    errored = [c for c in connectors if c.get("error")]
    calls = sum(c.get("calls_today", 0) for c in connectors)
    return {"connectors": len(connectors), "connected": len(connected), "errored": len(errored),
            "calls_today": calls, "healthy": len(errored) == 0}
