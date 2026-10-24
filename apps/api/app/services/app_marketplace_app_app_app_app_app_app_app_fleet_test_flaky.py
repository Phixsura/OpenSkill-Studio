"""Fleet test flakiness — track flaky test rate."""
from __future__ import annotations
def fleet_test_flakiness(tests: list[dict]) -> dict:
    flaky = [t for t in tests if t.get("flaky", False)]
    rate = round(len(flaky) / max(len(tests), 1) * 100, 2)
    return {"total": len(tests), "flaky": len(flaky), "flaky_rate_pct": rate,
            "acceptable": rate <= 1}
