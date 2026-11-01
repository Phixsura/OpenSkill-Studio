"""Fleet AI Saga Orchestrator — track distributed AI transaction sagas."""
from __future__ import annotations
def fleet_ai_saga_orchestrator(orchestrators: list[dict]) -> dict:
    active = [o for o in orchestrators if o.get("active", True)]
    sagas_24h = sum(o.get("sagas_24h", 0) for o in orchestrators)
    completed = sum(o.get("completed", 0) for o in orchestrators)
    compensated = sum(o.get("compensated", 0) for o in orchestrators)
    return {"orchestrators": len(orchestrators), "active": len(active), "sagas_24h": sagas_24h,
            "completed": completed, "compensated": compensated, "reliable": compensated < sagas_24h * 0.05 if sagas_24h > 0 else True}
