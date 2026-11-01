"""Fleet AI Model SLA v2 — track per-model service level agreements."""
from __future__ import annotations
def fleet_ai_model_sla_v2(slas: list[dict]) -> dict:
    active = [s for s in slas if s.get("active", True)]
    models = sum(s.get("models", 0) for s in slas)
    met = sum(s.get("met", 0) for s in slas)
    breached = sum(s.get("breached", 0) for s in slas)
    return {"slas": len(slas), "active": len(active), "models": models,
            "met": met, "breached": breached, "compliant": breached == 0}
