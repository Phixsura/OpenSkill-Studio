"""Fleet dependency vulnerability — scan dependency tree for CVEs."""
from __future__ import annotations
def fleet_dep_vuln_scan(deps: list[dict]) -> dict:
    critical = [d for d in deps if d.get("max_severity") == "critical"]
    high = [d for d in deps if d.get("max_severity") == "high"]
    total_cves = sum(d.get("cve_count", 0) for d in deps)
    return {"total_deps": len(deps), "critical": len(critical), "high": len(high),
            "total_cves": total_cves, "clean": len(critical) == 0 and len(high) == 0}
