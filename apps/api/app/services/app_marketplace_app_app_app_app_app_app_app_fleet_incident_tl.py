"""Fleet incident timeline — summarize incident history."""
from __future__ import annotations
def fleet_incident_timeline(incidents: list[dict]) -> dict:
    sev1 = [i for i in incidents if i.get("severity") == 1]
    sev2 = [i for i in incidents if i.get("severity") == 2]
    resolved = [i for i in incidents if i.get("resolved", False)]
    return {"total": len(incidents), "sev1": len(sev1), "sev2": len(sev2),
            "resolved": len(resolved), "open": len(incidents) - len(resolved)}
