"""Fleet evolution — track platform growth over time."""
from __future__ import annotations
def fleet_evolution(snapshots: list[dict]) -> dict:
    if len(snapshots) < 2:
        return {"growth": 0, "snapshots": len(snapshots)}
    first = snapshots[0].get("files", 0)
    last = snapshots[-1].get("files", 0)
    growth = round((last - first) / max(first, 1) * 100, 1)
    return {"first_files": first, "current_files": last, "growth_pct": growth,
            "snapshots": len(snapshots), "accelerating": growth > 100}
