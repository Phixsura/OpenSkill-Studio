"""API endpoint coverage — measure test coverage per endpoint."""
from __future__ import annotations


def calculate_coverage(endpoints: list[dict]) -> dict:
    covered = sum(1 for e in endpoints if e.get("has_test", False))
    total = len(endpoints)
    by_method: dict[str, dict] = {}
    for e in endpoints:
        method = e.get("method", "GET")
        if method not in by_method:
            by_method[method] = {"total": 0, "covered": 0}
        by_method[method]["total"] += 1
        if e.get("has_test"):
            by_method[method]["covered"] += 1
    uncovered = [e["path"] for e in endpoints if not e.get("has_test")]
    return {"total": total, "covered": covered, "uncovered_count": total - covered,
            "coverage_pct": round(covered / max(total, 1) * 100),
            "by_method": by_method, "uncovered_paths": uncovered[:10]}
