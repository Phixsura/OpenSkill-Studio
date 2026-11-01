"""Fleet TechDocs — track documentation-as-code coverage."""
from __future__ import annotations
def fleet_techdocs_status(services: list[dict]) -> dict:
    with_docs = [s for s in services if s.get("has_techdocs", False)]
    builds_ok = [s for s in with_docs if s.get("build_ok", True)]
    pct = round(len(with_docs) / max(len(services), 1) * 100, 1)
    return {"total": len(services), "with_techdocs": len(with_docs), "builds_ok": len(builds_ok),
            "coverage_pct": pct, "good": pct >= 80}
