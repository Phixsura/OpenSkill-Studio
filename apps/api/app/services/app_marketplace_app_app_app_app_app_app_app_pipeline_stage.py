"""Data pipeline stage executor — run and track pipeline stages."""
from __future__ import annotations
import time


def run_pipeline(stages: list[dict]) -> dict:
    results = []
    failed_at = None
    for i, stage in enumerate(stages):
        if failed_at is not None:
            results.append({"name": stage["name"], "status": "skipped", "duration_ms": 0})
            continue
        fn = stage.get("fn")
        start = time.monotonic()
        try:
            output = fn() if fn else {"ok": True}
            dur = round((time.monotonic() - start) * 1000, 1)
            results.append({"name": stage["name"], "status": "success",
                            "duration_ms": dur, "output": output})
        except Exception as e:
            dur = round((time.monotonic() - start) * 1000, 1)
            failed_at = i
            results.append({"name": stage["name"], "status": "failed",
                            "duration_ms": dur, "error": str(e)})
    total_ms = sum(r["duration_ms"] for r in results)
    passed = sum(1 for r in results if r["status"] == "success")
    return {"stages": results, "total_stages": len(stages), "passed": passed,
            "failed": failed_at is not None, "total_ms": round(total_ms, 1)}
