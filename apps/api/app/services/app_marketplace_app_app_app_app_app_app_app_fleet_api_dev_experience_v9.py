"""Fleet API Dev Experience v9 — track developer experience metrics."""
from __future__ import annotations
def fleet_api_dev_experience_v9(metrics: list[dict]) -> dict:
    satisfaction = sum(m.get("satisfaction", 0) for m in metrics) / len(metrics) if metrics else 0
    ttfhw = sum(m.get("time_to_first_hello_min", 0) for m in metrics) / len(metrics) if metrics else 0
    doc_coverage = sum(m.get("doc_coverage_pct", 0) for m in metrics) / len(metrics) if metrics else 0
    return {"metrics": len(metrics), "avg_satisfaction": round(satisfaction, 1),
            "avg_ttfhw_min": round(ttfhw, 1), "doc_coverage_pct": round(doc_coverage, 1),
            "healthy": satisfaction > 80}
