"""Fleet AI DevSecOps v8 — track ultimate security-first development."""
from __future__ import annotations
def fleet_ai_devsecops_v8(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    scans = sum(s.get("scans_24h", 0) for s in systems)
    vulns = sum(s.get("vulns", 0) for s in systems)
    fixed = sum(s.get("fixed", 0) for s in systems)
    sast = round(sum(s.get("sast_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "scans": scans,
            "vulns": vulns, "fixed": fixed, "sast": sast, "secure": vulns == fixed}
