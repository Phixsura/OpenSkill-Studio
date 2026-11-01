"""Fleet API WebSocket Auth v9 — track WebSocket authentication."""
from __future__ import annotations
def fleet_api_websocket_auth_v9(connections: list[dict]) -> dict:
    authenticated = [c for c in connections if c.get("authenticated")]
    token_based = [c for c in connections if c.get("auth_method") == "token"]
    rejected = sum(c.get("rejected_today", 0) for c in connections)
    return {"connections": len(connections), "authenticated": len(authenticated),
            "token_based": len(token_based), "rejected_today": rejected, "healthy": True}
