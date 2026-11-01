"""Fleet customer health — track customer success metrics."""
from __future__ import annotations
def fleet_customer_health(customers: list[dict]) -> dict:
    healthy = [c for c in customers if c.get("health_score", 0) >= 70]
    at_risk = [c for c in customers if 40 <= c.get("health_score", 0) < 70]
    churning = [c for c in customers if c.get("health_score", 0) < 40]
    return {"total": len(customers), "healthy": len(healthy), "at_risk": len(at_risk),
            "churning": len(churning), "health_rate": round(len(healthy) / max(len(customers), 1) * 100, 1)}
