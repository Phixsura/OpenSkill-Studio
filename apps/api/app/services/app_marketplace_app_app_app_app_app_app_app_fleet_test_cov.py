"""Fleet test coverage — aggregate test coverage across services."""
from __future__ import annotations
def fleet_test_coverage(services: list[dict]) -> dict:
    total_lines = sum(s.get("total_lines", 0) for s in services)
    covered_lines = sum(s.get("covered_lines", 0) for s in services)
    pct = round(covered_lines / max(total_lines, 1) * 100, 1)
    return {"total_lines": total_lines, "covered_lines": covered_lines,
            "coverage_pct": pct, "meets_target": pct >= 80}
