"""Fleet NATS — track NATS messaging server health."""
from __future__ import annotations
def fleet_nats_status(servers: list[dict]) -> dict:
    connected = [s for s in servers if s.get("connected", True)]
    total_subs = sum(s.get("subscriptions", 0) for s in servers)
    msgs_per_sec = sum(s.get("msgs_per_sec", 0) for s in servers)
    return {"servers": len(servers), "connected": len(connected), "subscriptions": total_subs,
            "msgs_per_sec": msgs_per_sec, "healthy": len(connected) == len(servers)}
