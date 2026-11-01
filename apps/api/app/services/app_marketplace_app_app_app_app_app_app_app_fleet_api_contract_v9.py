"""Fleet API Contract v9 — track API contract testing and versioning."""
from __future__ import annotations
def fleet_api_contract_v9(contracts: list[dict]) -> dict:
    verified = [c for c in contracts if c.get("verified")]
    breaking = [c for c in contracts if c.get("breaking_change")]
    consumers = sum(c.get("consumers", 0) for c in contracts)
    return {"contracts": len(contracts), "verified": len(verified), "breaking_changes": len(breaking),
            "total_consumers": consumers, "healthy": len(breaking) == 0}
