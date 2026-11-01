"""Data pipeline monitor — monitor ETL pipeline health and throughput."""
from __future__ import annotations
from collections import defaultdict


def monitor_pipeline(runs: list[dict]) -> dict:
    by_status: dict[str, int] = defaultdict(int)
    total_rows = 0
    total_ms = 0
    for r in runs:
        by_status[r.get("status", "unknown")] += 1
        total_rows += r.get("rows_processed", 0)
        total_ms += r.get("duration_ms", 0)
    success_rate = round(by_status.get("success", 0) / max(len(runs), 1) * 100, 1)
    avg_ms = round(total_ms / max(len(runs), 1), 1)
    throughput = round(total_rows / max(total_ms / 1000, 0.001)) if total_ms > 0 else 0
    return {"total_runs": len(runs), "by_status": dict(by_status),
            "success_rate": success_rate, "total_rows": total_rows,
            "avg_duration_ms": avg_ms, "throughput_rows_per_sec": throughput,
            "healthy": success_rate >= 95}


def stale_pipelines(pipelines: list[dict], max_age_hours: int = 24) -> list[dict]:
    stale = []
    for p in pipelines:
        age_hours = p.get("hours_since_last_run", 0)
        if age_hours > max_age_hours:
            stale.append({"name": p["name"], "hours_since": age_hours,
                          "overdue_by": age_hours - max_age_hours})
    return sorted(stale, key=lambda s: -s["hours_since"])
