"""Fleet AI Documentation v7 — track AI platform documentation quality."""
from __future__ import annotations
def fleet_ai_docs_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    pages = sum(s.get("pages", 0) for s in systems)
    examples = sum(s.get("examples", 0) for s in systems)
    satisfaction = round(sum(s.get("satisfaction_pct", 0) for s in systems) / max(len(systems), 1), 1)
    coverage = round(sum(s.get("coverage_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "pages": pages,
            "examples": examples, "satisfaction": satisfaction, "coverage": coverage, "comprehensive": coverage > 90}
