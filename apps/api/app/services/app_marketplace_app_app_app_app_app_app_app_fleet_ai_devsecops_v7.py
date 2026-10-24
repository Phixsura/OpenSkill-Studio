"""Fleet AI DevSecOps v7 — track security-first development operations."""
from __future__ import annotations
def fleet_ai_devsecops_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    scans_24h = sum(s.get("scans", 0) for s in systems)
    vulns_found = sum(s.get("vulns", 0) for s in systems)
    vulns_fixed = sum(s.get("fixed", 0) for s in systems)
    sast_coverage = round(sum(s.get("sast_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "scans": scans_24h,
            "vulns": vulns_found, "fixed": vulns_fixed, "sast_pct": sast_coverage, "secure": vulns_found == vulns_fixed}
