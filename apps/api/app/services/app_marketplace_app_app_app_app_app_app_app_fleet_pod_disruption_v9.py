"""Fleet Pod Disruption v9 — track PDB compliance and voluntary disruptions."""
from __future__ import annotations
def fleet_pod_disruption_v9(pdbs: list[dict]) -> dict:
    compliant = [p for p in pdbs if p.get("compliant", True)]
    disruptions = sum(p.get("disruptions_today", 0) for p in pdbs)
    min_available = sum(p.get("min_available", 0) for p in pdbs)
    return {"total_pdbs": len(pdbs), "compliant": len(compliant), "disruptions_today": disruptions,
            "min_available_total": min_available, "healthy": len(compliant) == len(pdbs)}
