"""Fleet AI Status v9 — track ultimate platform operational status."""
from __future__ import annotations
def fleet_ai_status_v9(systems: list[dict]) -> dict:
    total = len(systems)
    operational = sum(1 for s in systems if s.get("status") == "operational")
    uptime = round(sum(s.get("uptime_pct", 0) for s in systems) / max(total, 1), 4)
    return {"total": total, "operational": operational, "uptime": uptime,
            "status": "🟢 ALL OPERATIONAL" if operational == total else "🟡 DEGRADED"}
