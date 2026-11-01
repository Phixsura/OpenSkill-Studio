"""Fleet dependency freshness — track outdated dependencies."""
from __future__ import annotations
def fleet_dep_freshness(deps: list[dict]) -> dict:
    outdated = [d for d in deps if d.get("versions_behind", 0) > 0]
    critical = [d for d in deps if d.get("versions_behind", 0) >= 3]
    return {"total": len(deps), "outdated": len(outdated),
            "critical": len(critical), "up_to_date": len(outdated) == 0}
