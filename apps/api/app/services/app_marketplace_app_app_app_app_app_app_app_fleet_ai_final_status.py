"""Fleet AI Platform Final Status — track comprehensive platform operational status."""
from __future__ import annotations
def fleet_ai_final_status(systems: list[dict]) -> dict:
    total = len(systems)
    operational = sum(1 for s in systems if s.get("status") == "operational")
    degraded = sum(1 for s in systems if s.get("status") == "degraded")
    down = sum(1 for s in systems if s.get("status") == "down")
    uptime = round(sum(s.get("uptime_pct", 0) for s in systems) / max(total, 1), 3)
    return {"total": total, "operational": operational, "degraded": degraded,
            "down": down, "uptime": uptime, "status": "🟢 ALL OPERATIONAL" if down == 0 and degraded == 0 else "🟡 DEGRADED"}
