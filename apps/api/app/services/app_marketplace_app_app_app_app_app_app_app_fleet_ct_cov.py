"""Fleet contract test coverage — track API contract test adoption."""
from __future__ import annotations
def fleet_contract_test_coverage(apis: list[dict]) -> dict:
    with_ct = [a for a in apis if a.get("has_contract_tests", False)]
    pct = round(len(with_ct) / max(len(apis), 1) * 100, 1)
    return {"total": len(apis), "with_tests": len(with_ct), "without": len(apis) - len(with_ct),
            "coverage_pct": pct, "good": pct >= 80}
