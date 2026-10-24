"""Fleet data locality — track data residency compliance."""
from __future__ import annotations
def fleet_data_locality(datasets: list[dict]) -> dict:
    compliant = [d for d in datasets if d.get("region_compliant", True)]
    violations = len(datasets) - len(compliant)
    return {"total": len(datasets), "compliant": len(compliant),
            "violations": violations, "fully_compliant": violations == 0}
