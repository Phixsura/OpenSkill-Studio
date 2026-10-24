"""Fleet severity distribution — track incident severity breakdown."""
from __future__ import annotations
def fleet_severity_dist(incidents: list[dict]) -> dict:
    by_sev: dict[int, int] = {}
    for i in incidents:
        s = i.get("severity", 3)
        by_sev[s] = by_sev.get(s, 0) + 1
    return {"total": len(incidents), "by_severity": by_sev,
            "sev1_count": by_sev.get(1, 0), "critical": by_sev.get(1, 0) > 0}
