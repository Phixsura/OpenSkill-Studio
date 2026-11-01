"""Fleet technical debt — quantify tech debt across services."""
from __future__ import annotations
def fleet_tech_debt(services: list[dict]) -> dict:
    total_debt_hours = sum(s.get("debt_hours", 0) for s in services)
    high_debt = [s for s in services if s.get("debt_hours", 0) > 100]
    avg = round(total_debt_hours / max(len(services), 1), 1)
    return {"total_debt_hours": total_debt_hours, "high_debt_services": len(high_debt),
            "avg_per_service": avg, "manageable": avg <= 50}
