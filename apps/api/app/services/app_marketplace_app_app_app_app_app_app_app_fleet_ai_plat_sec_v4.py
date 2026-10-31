"""Fleet AI Security v4 — track zero-trust AI platform security."""
from __future__ import annotations
def fleet_ai_security_v4(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    score = round(sum(s.get("score", 0) for s in systems) / max(len(systems), 1), 1)
    threats_blocked = sum(s.get("threats", 0) for s in systems)
    zero_trust = all(s.get("zero_trust", False) for s in systems)
    encrypted_pct = round(sum(s.get("encrypted_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "score": score,
            "threats": threats_blocked, "zero_trust": zero_trust, "encrypted_pct": encrypted_pct, "hardened": score > 95}
