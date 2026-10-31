"""Fleet service catalog — service ownership and metadata."""
from __future__ import annotations
def fleet_svc_catalog(services: list[dict]) -> dict:
    with_owner = [s for s in services if s.get("owner")]
    with_docs = [s for s in services if s.get("has_docs", False)]
    with_runbook = [s for s in services if s.get("has_runbook", False)]
    return {"total": len(services), "with_owner": len(with_owner),
            "with_docs": len(with_docs), "with_runbook": len(with_runbook),
            "completeness_pct": round((len(with_owner) + len(with_docs) + len(with_runbook)) / max(len(services) * 3, 1) * 100, 1)}
