"""Fleet capacity reservation — track reserved vs used capacity."""
from __future__ import annotations
def fleet_capacity_reservation(reservations: list[dict]) -> dict:
    total_reserved = sum(r.get("reserved_units", 0) for r in reservations)
    total_used = sum(r.get("used_units", 0) for r in reservations)
    util = round(total_used / max(total_reserved, 1) * 100, 1)
    return {"reserved": total_reserved, "used": total_used, "util_pct": util,
            "waste": util < 50}
