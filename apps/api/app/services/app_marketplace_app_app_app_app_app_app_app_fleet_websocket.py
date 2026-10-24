"""Fleet WebSocket metrics — track WS connection health."""
from __future__ import annotations
def fleet_websocket_metrics(servers: list[dict]) -> dict:
    total_conns = sum(s.get("connections", 0) for s in servers)
    max_conns = sum(s.get("max_connections", 0) for s in servers)
    pct = round(total_conns / max(max_conns, 1) * 100, 1)
    errors = sum(s.get("errors_per_min", 0) for s in servers)
    return {"connections": total_conns, "max_connections": max_conns, "util_pct": pct,
            "errors_per_min": errors, "healthy": errors == 0 and pct < 90}
