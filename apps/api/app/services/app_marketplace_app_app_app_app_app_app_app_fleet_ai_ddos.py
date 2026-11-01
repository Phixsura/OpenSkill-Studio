"""Fleet AI DDoS Protection — track AI endpoint DDoS mitigation."""
from __future__ import annotations
def fleet_ai_ddos_protection(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    attacks_mitigated = sum(s.get("attacks", 0) for s in systems)
    peak_gbps = max((s.get("peak_gbps", 0) for s in systems), default=0)
    uptime_pct = round(sum(s.get("uptime_pct", 0) for s in systems) / max(len(systems), 1), 3)
    return {"systems": len(systems), "active": len(active), "attacks": attacks_mitigated,
            "peak_gbps": peak_gbps, "uptime_pct": uptime_pct, "resilient": uptime_pct > 99.99}
