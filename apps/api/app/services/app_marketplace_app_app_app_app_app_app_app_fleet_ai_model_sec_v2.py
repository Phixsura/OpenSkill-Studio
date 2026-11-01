"""Fleet AI Model Security v2 — track model access security and protection."""
from __future__ import annotations
def fleet_ai_model_security_v2(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    models_protected = sum(s.get("models", 0) for s in systems)
    threats_blocked = sum(s.get("threats", 0) for s in systems)
    encryption_pct = round(sum(s.get("encrypted_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "models": models_protected,
            "threats": threats_blocked, "encrypted_pct": encryption_pct, "secure": encryption_pct == 100}
