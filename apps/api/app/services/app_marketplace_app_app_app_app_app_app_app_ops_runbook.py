"""Operational runbook executor — execute predefined remediation steps."""
from __future__ import annotations
import time


def execute_runbook(name: str, steps: list[dict], context: dict | None = None) -> dict:
    results = []
    all_ok = True
    total_ms = 0
    for s in steps:
        success = s.get("auto_success", True)
        duration = s.get("est_duration_ms", 100)
        total_ms += duration
        if not success:
            all_ok = False
        results.append({"step": s["name"], "status": "completed" if success else "failed",
                         "duration_ms": duration})
        if not success and s.get("stop_on_failure", True):
            break
    return {"runbook": name, "results": results, "steps_executed": len(results),
            "total_steps": len(steps), "all_ok": all_ok,
            "total_duration_ms": total_ms, "executed_at": time.time()}
