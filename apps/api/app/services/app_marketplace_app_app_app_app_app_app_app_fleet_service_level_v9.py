"""Fleet Service Level v9 — track SLI/SLO/SLA hierarchy."""
from __future__ import annotations
def fleet_service_level_v9(objectives: list[dict]) -> dict:
    met = [o for o in objectives if o.get("met")]
    at_risk = [o for o in objectives if o.get("at_risk")]
    breached = [o for o in objectives if o.get("breached")]
    return {"total": len(objectives), "met": len(met), "at_risk": len(at_risk),
            "breached": len(breached), "healthy": len(breached) == 0}
