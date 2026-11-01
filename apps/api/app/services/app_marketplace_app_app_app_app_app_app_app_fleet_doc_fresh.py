"""Fleet doc freshness — track documentation staleness."""
from __future__ import annotations
def fleet_doc_freshness(docs: list[dict]) -> dict:
    fresh = [d for d in docs if d.get("age_days", 0) <= 90]
    stale = len(docs) - len(fresh)
    return {"total": len(docs), "fresh": len(fresh), "stale": stale,
            "freshness_pct": round(len(fresh) / max(len(docs), 1) * 100, 1)}
