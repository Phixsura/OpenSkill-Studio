"""Fleet saga orchestrator — track distributed saga status."""
from __future__ import annotations
def fleet_saga_status(sagas: list[dict]) -> dict:
    completed = [s for s in sagas if s.get("status") == "completed"]
    compensating = [s for s in sagas if s.get("status") == "compensating"]
    failed = [s for s in sagas if s.get("status") == "failed"]
    return {"total": len(sagas), "completed": len(completed), "compensating": len(compensating),
            "failed": len(failed), "healthy": len(failed) == 0 and len(compensating) == 0}
