"""Fleet contract testing — track consumer-driven contract results."""
from __future__ import annotations
def fleet_contract_tests(contracts: list[dict]) -> dict:
    passing = [c for c in contracts if c.get("status") == "pass"]
    broken = [c for c in contracts if c.get("status") == "broken"]
    return {"total": len(contracts), "passing": len(passing), "broken": len(broken),
            "compatible": len(broken) == 0}
