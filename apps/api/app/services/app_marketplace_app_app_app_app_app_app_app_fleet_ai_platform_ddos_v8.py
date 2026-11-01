"""Fleet AI DDoS v8 — track ultimate DDoS mitigation."""
from __future__ import annotations
def fleet_ai_ddos_v8(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    attacks = sum(s.get("attacks_mitigated", 0) for s in systems)
    peak_tbps = max((s.get("peak_tbps", 0) for s in systems), default=0)
    uptime = round(sum(s.get("uptime_pct", 0) for s in systems) / max(len(systems), 1), 4)
    return {"systems": len(systems), "active": len(active), "attacks": attacks,
            "peak_tbps": peak_tbps, "uptime": uptime, "impenetrable": uptime > 99.999}
