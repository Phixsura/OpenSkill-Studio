"""Fleet AI Security v8 — track ultimate zero-trust security at hyperscale."""
from __future__ import annotations
def fleet_ai_security_v8(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    score = round(sum(s.get("score", 0) for s in systems) / max(len(systems), 1), 1)
    threats = sum(s.get("threats_blocked", 0) for s in systems)
    zero_trust = all(s.get("zt", False) for s in systems)
    encrypted = round(sum(s.get("encrypted_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "score": score,
            "threats": threats, "zero_trust": zero_trust, "encrypted": encrypted, "hardened": score > 97 and zero_trust}
