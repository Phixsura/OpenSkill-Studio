"""Fleet Bun — track Bun runtime performance."""
from __future__ import annotations
def fleet_bun_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running", True)]
    total_rps = sum(a.get("rps", 0) for a in apps)
    startup_ms = round(sum(a.get("startup_ms", 0) for a in apps) / max(len(apps), 1), 1)
    return {"apps": len(apps), "running": len(running), "rps": total_rps,
            "avg_startup_ms": startup_ms, "instant": startup_ms < 50}
