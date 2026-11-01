"""Fleet AI DDoS v4 — track AI-powered DDoS mitigation at scale."""
from __future__ import annotations
def fleet_ai_ddos_v4(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    attacks_mitigated = sum(s.get("attacks", 0) for s in systems)
    peak_tbps = max((s.get("peak_tbps", 0) for s in systems), default=0)
    uptime = round(sum(s.get("uptime_pct", 0) for s in systems) / max(len(systems), 1), 4)
    return {"systems": len(systems), "active": len(active), "attacks": attacks_mitigated,
            "peak_tbps": peak_tbps, "uptime": uptime, "impenetrable": uptime > 99.999}
