"""Fleet Threat Intel v9 — track threat intelligence feeds and IOCs."""
from __future__ import annotations
def fleet_threat_intel_v9(feeds: list[dict]) -> dict:
    active = [f for f in feeds if f.get("active")]
    iocs = sum(f.get("iocs_today", 0) for f in feeds)
    blocked = sum(f.get("blocked_today", 0) for f in feeds)
    return {"feeds": len(feeds), "active": len(active), "iocs_today": iocs,
            "blocked_today": blocked, "healthy": len(active) == len(feeds)}
