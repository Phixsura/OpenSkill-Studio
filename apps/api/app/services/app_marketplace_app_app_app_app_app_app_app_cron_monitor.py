"""Cron job monitor — track cron job execution health."""
from __future__ import annotations
import time


def record_execution(job_name: str, success: bool, duration_sec: float,
                      output: str = "") -> dict:
    return {"job_name": job_name, "success": success, "duration_sec": round(duration_sec, 2),
            "output_length": len(output), "executed_at": time.time()}


def analyze_job_health(executions: list[dict]) -> dict:
    if not executions:
        return {"runs": 0, "success_rate": 0, "avg_duration": 0}
    succeeded = sum(1 for e in executions if e["success"])
    durations = [e["duration_sec"] for e in executions]
    failures_in_row = 0
    for e in reversed(executions):
        if not e["success"]:
            failures_in_row += 1
        else:
            break
    return {"runs": len(executions), "succeeded": succeeded,
            "failed": len(executions) - succeeded,
            "success_rate": round(succeeded / len(executions) * 100),
            "avg_duration": round(sum(durations) / len(durations), 2),
            "max_duration": max(durations),
            "consecutive_failures": failures_in_row,
            "healthy": failures_in_row < 3}
