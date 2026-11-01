"""Fleet mock server — track mock server usage for testing."""
from __future__ import annotations
def fleet_mock_server(mocks: list[dict]) -> dict:
    active = [m for m in mocks if m.get("active", False)]
    total_hits = sum(m.get("hits_24h", 0) for m in mocks)
    return {"total": len(mocks), "active": len(active), "hits_24h": total_hits,
            "well_used": total_hits > 1000}
