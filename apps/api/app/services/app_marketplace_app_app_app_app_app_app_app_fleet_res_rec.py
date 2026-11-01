"""Fleet resource recommendation — suggest right-sizing actions."""
from __future__ import annotations
def fleet_resource_recommendations(containers: list[dict]) -> dict:
    over = [c for c in containers if c.get("cpu_usage_pct", 0) < 20 and c.get("cpu_request_mcpu", 0) > 100]
    under = [c for c in containers if c.get("cpu_usage_pct", 0) > 90]
    return {"total": len(containers), "over_provisioned": len(over),
            "under_provisioned": len(under), "right_sized": len(containers) - len(over) - len(under),
            "savings_possible": len(over) > 0}
