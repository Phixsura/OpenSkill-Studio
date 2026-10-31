"""Fleet metric cardinality — track metric series count."""
from __future__ import annotations
def fleet_metric_cardinality(sources: list[dict]) -> dict:
    total = sum(s.get("series_count", 0) for s in sources)
    high_card = [s for s in sources if s.get("series_count", 0) > 100000]
    return {"total_series": total, "sources": len(sources),
            "high_cardinality": len(high_card), "warning": total > 1000000}
