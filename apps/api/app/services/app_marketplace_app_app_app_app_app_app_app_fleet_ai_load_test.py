"""Fleet AI Load Test — track AI endpoint performance under load."""
from __future__ import annotations
def fleet_ai_load_test(testers: list[dict]) -> dict:
    active = [t for t in testers if t.get("active", True)]
    tests_24h = sum(t.get("tests_24h", 0) for t in testers)
    max_rps = max((t.get("max_rps", 0) for t in testers), default=0)
    p99_ms = round(sum(t.get("p99_ms", 0) for t in testers) / max(len(testers), 1), 1)
    error_pct = round(sum(t.get("error_pct", 0) for t in testers) / max(len(testers), 1), 2)
    return {"testers": len(testers), "active": len(active), "tests_24h": tests_24h,
            "max_rps": max_rps, "p99_ms": p99_ms, "error_pct": error_pct, "performant": p99_ms < 200}
