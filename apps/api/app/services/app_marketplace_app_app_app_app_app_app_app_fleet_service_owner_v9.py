"""Fleet Service Owner v9 — track service ownership and accountability."""
from __future__ import annotations
def fleet_service_owner_v9(services: list[dict]) -> dict:
    with_owner = [s for s in services if s.get("owner")]
    with_oncall = [s for s in services if s.get("oncall")]
    with_runbook = [s for s in services if s.get("runbook")]
    return {"services": len(services), "with_owner": len(with_owner), "with_oncall": len(with_oncall),
            "with_runbook": len(with_runbook), "healthy": len(with_owner) == len(services)}
