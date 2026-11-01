"""Integration test runner — execute and report integration tests."""
from __future__ import annotations
import time


def run_suite(name: str, tests: list[dict]) -> dict:
    results = []
    passed = 0
    failed = 0
    skipped = 0
    total_ms = 0
    for t in tests:
        status = t.get("status", "passed")
        dur = t.get("duration_ms", 0)
        total_ms += dur
        if status == "passed":
            passed += 1
        elif status == "failed":
            failed += 1
        else:
            skipped += 1
        results.append({"name": t["name"], "status": status,
                        "duration_ms": dur, "error": t.get("error", "")})
    return {"suite": name, "results": results, "total": len(tests),
            "passed": passed, "failed": failed, "skipped": skipped,
            "duration_ms": total_ms, "success": failed == 0,
            "pass_rate": round(passed / max(len(tests), 1) * 100)}


def compare_runs(current: dict, previous: dict) -> dict:
    new_failures = []
    fixed = []
    cur_map = {r["name"]: r["status"] for r in current.get("results", [])}
    prev_map = {r["name"]: r["status"] for r in previous.get("results", [])}
    for name, status in cur_map.items():
        prev_status = prev_map.get(name, "new")
        if status == "failed" and prev_status == "passed":
            new_failures.append(name)
        elif status == "passed" and prev_status == "failed":
            fixed.append(name)
    return {"new_failures": new_failures, "fixed": fixed,
            "regression": len(new_failures) > 0,
            "improvement": len(fixed) > 0}
