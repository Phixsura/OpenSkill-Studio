"""Fleet AI Security v6 — track zero-trust security posture."""
from __future__ import annotations
def fleet_ai_security_v6(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    score = round(sum(s.get("score", 0) for s in systems) / max(len(systems), 1), 1)
    threats = sum(s.get("threats_blocked", 0) for s in systems)
    zero_trust = all(s.get("zt", False) for s in systems)
    return {"systems": len(systems), "active": len(active), "score": score,
            "threats": threats, "zero_trust": zero_trust, "hardened": score > 95 and zero_trust}
