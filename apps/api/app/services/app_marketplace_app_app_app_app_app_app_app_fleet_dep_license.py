"""Fleet dependency license — audit dependency licenses."""
from __future__ import annotations
def fleet_dep_license(deps: list[dict]) -> dict:
    approved = [d for d in deps if d.get("license_approved", True)]
    copyleft = [d for d in deps if d.get("license_type") == "copyleft"]
    unknown = [d for d in deps if d.get("license_type") == "unknown"]
    return {"total": len(deps), "approved": len(approved), "copyleft": len(copyleft),
            "unknown": len(unknown), "compliant": len(unknown) == 0 and len(copyleft) == 0}
