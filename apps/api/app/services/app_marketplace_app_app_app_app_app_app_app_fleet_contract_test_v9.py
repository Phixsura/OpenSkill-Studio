"""Fleet Contract Test v9 — track consumer-driven contract testing."""
from __future__ import annotations
def fleet_contract_test_v9(contracts: list[dict]) -> dict:
    verified = [c for c in contracts if c.get("verified")]
    broken = [c for c in contracts if c.get("broken")]
    consumers = len({c.get("consumer") for c in contracts if c.get("consumer")})
    return {"contracts": len(contracts), "verified": len(verified), "broken": len(broken),
            "consumers": consumers, "healthy": len(broken) == 0}
