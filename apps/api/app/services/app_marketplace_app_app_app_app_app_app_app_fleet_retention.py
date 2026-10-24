"""Fleet data retention — track data retention policy compliance."""
from __future__ import annotations
def fleet_data_retention(datasets: list[dict]) -> dict:
    compliant = [d for d in datasets if d.get("within_policy", True)]
    overdue = [d for d in datasets if not d.get("within_policy", True)]
    return {"total": len(datasets), "compliant": len(compliant),
            "overdue": len(overdue), "all_compliant": len(overdue) == 0}
