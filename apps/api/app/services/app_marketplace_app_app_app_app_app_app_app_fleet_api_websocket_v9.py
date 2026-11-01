"""Fleet API WebSocket v9 — track WebSocket connection management."""
from __future__ import annotations
def fleet_api_websocket_v9(endpoints: list[dict]) -> dict:
    active_conns = sum(e.get("connections", 0) for e in endpoints)
    messages_sec = sum(e.get("messages_per_sec", 0) for e in endpoints)
    errors = sum(e.get("errors_today", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "active_connections": active_conns,
            "messages_per_sec": messages_sec, "errors": errors, "healthy": errors == 0}
