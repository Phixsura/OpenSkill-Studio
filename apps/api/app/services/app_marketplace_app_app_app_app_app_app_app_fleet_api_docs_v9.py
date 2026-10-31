"""Fleet API Docs v9 — track API documentation coverage and freshness."""
from __future__ import annotations
def fleet_api_docs_v9(endpoints: list[dict]) -> dict:
    documented = [e for e in endpoints if e.get("documented")]
    stale = [e for e in endpoints if e.get("stale_docs")]
    coverage = round(len(documented) / len(endpoints) * 100, 1) if endpoints else 0
    return {"endpoints": len(endpoints), "documented": len(documented), "stale": len(stale),
            "coverage_pct": coverage, "healthy": coverage > 95}
