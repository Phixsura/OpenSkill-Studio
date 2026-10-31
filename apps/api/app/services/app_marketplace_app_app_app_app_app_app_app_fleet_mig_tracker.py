"""Fleet migration tracker — track ongoing platform migrations."""
from __future__ import annotations
def fleet_migration_tracker(migrations: list[dict]) -> dict:
    completed = [m for m in migrations if m.get("status") == "completed"]
    in_progress = [m for m in migrations if m.get("status") == "in_progress"]
    blocked = [m for m in migrations if m.get("status") == "blocked"]
    return {"total": len(migrations), "completed": len(completed),
            "in_progress": len(in_progress), "blocked": len(blocked),
            "all_done": len(completed) == len(migrations)}
