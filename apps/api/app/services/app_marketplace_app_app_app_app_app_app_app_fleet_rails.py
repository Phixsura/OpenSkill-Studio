"""Fleet Rails — track Ruby on Rails application health."""
from __future__ import annotations
def fleet_rails_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running", True)]
    total_rps = sum(a.get("rps", 0) for a in apps)
    db_pool_pct = round(sum(a.get("db_pool_pct", 0) for a in apps) / max(len(apps), 1), 1)
    return {"apps": len(apps), "running": len(running), "rps": total_rps,
            "db_pool_pct": db_pool_pct, "healthy": db_pool_pct < 80}
