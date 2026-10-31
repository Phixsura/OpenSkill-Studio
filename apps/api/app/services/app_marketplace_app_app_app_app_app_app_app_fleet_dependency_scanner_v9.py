"""Fleet Dependency Scanner v9 — track dependency vulnerabilities and updates."""
from __future__ import annotations
def fleet_dependency_scanner_v9(deps: list[dict]) -> dict:
    vulnerable = [d for d in deps if d.get("vulnerable")]
    outdated = [d for d in deps if d.get("outdated")]
    critical = [d for d in deps if d.get("severity") == "critical"]
    return {"total_deps": len(deps), "vulnerable": len(vulnerable), "outdated": len(outdated),
            "critical": len(critical), "healthy": len(critical) == 0}
