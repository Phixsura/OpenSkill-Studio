"""Fleet API Conformance v9 — track API standards conformance testing."""
from __future__ import annotations
def fleet_api_conformance_v9(tests: list[dict]) -> dict:
    passed = [t for t in tests if t.get("passed")]
    standards = len({t.get("standard") for t in tests if t.get("standard")})
    violations = sum(t.get("violations", 0) for t in tests)
    return {"tests": len(tests), "passed": len(passed), "standards": standards,
            "violations": violations, "healthy": violations == 0}
