"""Fleet Uptime Monitor v9 — track endpoint uptime and response time."""
from __future__ import annotations
def fleet_uptime_monitor_v9(monitors: list[dict]) -> dict:
    up = [m for m in monitors if m.get("status") == "up"]
    down = [m for m in monitors if m.get("status") == "down"]
    avg_response = sum(m.get("response_ms", 0) for m in monitors) / len(monitors) if monitors else 0
    uptime_pct = len(up) / len(monitors) * 100 if monitors else 0
    return {"monitors": len(monitors), "up": len(up), "down": len(down),
            "avg_response_ms": round(avg_response, 1), "uptime_pct": round(uptime_pct, 2),
            "healthy": len(down) == 0}
