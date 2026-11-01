"""Fleet AI Platform Migration v2 — track cross-region platform migration."""
from __future__ import annotations
def fleet_ai_platform_migration_v2(migrations: list[dict]) -> dict:
    active = [m for m in migrations if m.get("status") == "running"]
    completed = [m for m in migrations if m.get("status") == "completed"]
    data_tb = round(sum(m.get("data_tb", 0) for m in migrations), 1)
    zero_downtime = all(m.get("zero_dt", False) for m in completed) if completed else True
    return {"migrations": len(migrations), "running": len(active), "completed": len(completed),
            "data_tb": data_tb, "zero_downtime": zero_downtime, "smooth": zero_downtime}
