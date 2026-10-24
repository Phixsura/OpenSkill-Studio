"""Fleet data quality — track data quality metrics."""
from __future__ import annotations
def fleet_data_quality(datasets: list[dict]) -> dict:
    good = [d for d in datasets if d.get("quality_score", 0) >= 90]
    poor = [d for d in datasets if d.get("quality_score", 0) < 70]
    avg = round(sum(d.get("quality_score", 0) for d in datasets) / max(len(datasets), 1), 1)
    return {"total": len(datasets), "good": len(good), "poor": len(poor),
            "avg_score": avg, "high_quality": avg >= 90}
