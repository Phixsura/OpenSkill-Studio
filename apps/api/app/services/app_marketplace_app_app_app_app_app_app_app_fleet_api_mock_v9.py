"""Fleet API Mock v9 — track mock service instances for testing."""
from __future__ import annotations
def fleet_api_mock_v9(mocks: list[dict]) -> dict:
    active = [m for m in mocks if m.get("active")]
    requests_served = sum(m.get("requests", 0) for m in mocks)
    endpoints = sum(m.get("endpoints", 0) for m in mocks)
    return {"mocks": len(mocks), "active": len(active), "requests_served": requests_served,
            "endpoints": endpoints, "healthy": True}
