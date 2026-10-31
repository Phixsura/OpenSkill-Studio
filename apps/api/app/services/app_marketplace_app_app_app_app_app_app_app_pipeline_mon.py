"""Data pipeline monitor — track ETL pipeline health and throughput."""
from __future__ import annotations


def monitor_pipeline(name: str, stages: list[dict]) -> dict:
    total_records = 0
    total_errors = 0
    bottleneck = None
    max_time = 0
    results = []
    for s in stages:
        records = s.get("records_processed", 0)
        errors = s.get("errors", 0)
        duration_sec = s.get("duration_sec", 0)
        total_records += records
        total_errors += errors
        if duration_sec > max_time:
            max_time = duration_sec
            bottleneck = s.get("name", "")
        throughput = round(records / max(duration_sec, 0.01))
        results.append({"name": s.get("name", ""), "records": records, "errors": errors,
                         "duration_sec": duration_sec, "throughput_rps": throughput})
    healthy = total_errors == 0
    return {"pipeline": name, "stages": results, "total_records": total_records,
            "total_errors": total_errors, "healthy": healthy,
            "bottleneck": bottleneck}


def pipeline_summary(pipelines: list[dict]) -> dict:
    healthy = sum(1 for p in pipelines if p["healthy"])
    total_records = sum(p["total_records"] for p in pipelines)
    return {"total": len(pipelines), "healthy": healthy,
            "unhealthy": len(pipelines) - healthy,
            "total_records": total_records}
