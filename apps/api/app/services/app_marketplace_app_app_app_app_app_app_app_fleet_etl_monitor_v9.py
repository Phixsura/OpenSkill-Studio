"""Fleet ETL Monitor v9 — track ETL job execution and data quality."""
from __future__ import annotations
def fleet_etl_monitor_v9(jobs: list[dict]) -> dict:
    success = [j for j in jobs if j.get("status") == "success"]
    failed = [j for j in jobs if j.get("status") == "failed"]
    rows = sum(j.get("rows_processed", 0) for j in jobs)
    quality_score = sum(j.get("quality_score", 0) for j in jobs) / len(jobs) if jobs else 0
    return {"jobs": len(jobs), "success": len(success), "failed": len(failed),
            "rows_processed": rows, "avg_quality": round(quality_score, 1), "healthy": len(failed) == 0}
