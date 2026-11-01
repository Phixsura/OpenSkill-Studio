"""Fleet data pipeline lag — track ETL/streaming pipeline freshness."""
from __future__ import annotations
def fleet_pipeline_lag(pipelines: list[dict]) -> dict:
    lagging = [p for p in pipelines if p.get("lag_minutes", 0) > 15]
    max_lag = max((p.get("lag_minutes", 0) for p in pipelines), default=0)
    return {"total": len(pipelines), "lagging": len(lagging),
            "max_lag_min": max_lag, "fresh": len(lagging) == 0}
