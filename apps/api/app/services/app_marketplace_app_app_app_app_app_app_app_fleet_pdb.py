"""Fleet PDB status — pod disruption budget compliance."""
from __future__ import annotations
def fleet_pdb_status(pdbs: list[dict]) -> dict:
    violated = [p for p in pdbs if p.get("disruptions_allowed", 1) == 0]
    return {"total": len(pdbs), "violated": len(violated),
            "compliant": len(pdbs) - len(violated), "all_compliant": len(violated) == 0}
