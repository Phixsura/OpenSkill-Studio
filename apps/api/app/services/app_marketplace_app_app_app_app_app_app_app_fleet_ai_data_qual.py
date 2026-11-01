"""Fleet AI Data Quality — track training data quality monitoring."""
from __future__ import annotations
def fleet_ai_data_quality(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active", True)]
    datasets_monitored = sum(m.get("datasets", 0) for m in monitors)
    checks_24h = sum(m.get("checks_24h", 0) for m in monitors)
    quality_score = round(sum(m.get("quality", 0) for m in monitors) / max(len(monitors), 1), 1)
    return {"monitors": len(monitors), "active": len(active), "datasets": datasets_monitored,
            "checks_24h": checks_24h, "quality": quality_score, "high_quality": quality_score > 90}
