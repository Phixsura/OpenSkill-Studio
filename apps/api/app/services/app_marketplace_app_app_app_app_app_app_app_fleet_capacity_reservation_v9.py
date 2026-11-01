"""Fleet Capacity Reservation v9 — track reserved compute capacity."""
from __future__ import annotations
def fleet_capacity_reservation_v9(reservations: list[dict]) -> dict:
    active = [r for r in reservations if r.get("active")]
    utilized = sum(r.get("utilized_pct", 0) for r in reservations) / len(reservations) if reservations else 0
    savings = sum(r.get("monthly_savings", 0) for r in reservations)
    return {"reservations": len(reservations), "active": len(active), "avg_utilized_pct": round(utilized, 1),
            "monthly_savings": round(savings, 2), "healthy": utilized > 60}
