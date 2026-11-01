"""Fleet API response size — track response payload sizes."""
from __future__ import annotations
def fleet_response_size(endpoints: list[dict]) -> dict:
    avg_kb = round(sum(e.get("avg_response_kb", 0) for e in endpoints) / max(len(endpoints), 1), 1)
    large = [e for e in endpoints if e.get("avg_response_kb", 0) > 1024]
    return {"total": len(endpoints), "avg_response_kb": avg_kb,
            "large_responses": len(large), "optimized": len(large) == 0}
