"""Fleet SIEM Connector v9 — track security event forwarding."""
from __future__ import annotations
def fleet_siem_connector_v9(connectors: list[dict]) -> dict:
    active = [c for c in connectors if c.get("active", True)]
    events_fwd = sum(c.get("events_forwarded", 0) for c in connectors)
    dropped = sum(c.get("dropped", 0) for c in connectors)
    return {"connectors": len(connectors), "active": len(active), "events_forwarded": events_fwd,
            "dropped": dropped, "healthy": dropped == 0}
