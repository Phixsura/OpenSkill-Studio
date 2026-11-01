"""Fleet Django — track Python web framework health."""
from __future__ import annotations
def fleet_django_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running", True)]
    total_views = sum(a.get("views", 0) for a in apps)
    migrations_pending = sum(a.get("pending_migrations", 0) for a in apps)
    return {"apps": len(apps), "running": len(running), "views": total_views,
            "pending_migrations": migrations_pending, "up_to_date": migrations_pending == 0}
