"""Fleet API Request Priority v9 — track request priority queuing."""
from __future__ import annotations
def fleet_api_request_priority_v9(queues: list[dict]) -> dict:
    high = [q for q in queues if q.get("priority") == "high"]
    normal = [q for q in queues if q.get("priority") == "normal"]
    low = [q for q in queues if q.get("priority") == "low"]
    total = sum(q.get("requests_today", 0) for q in queues)
    return {"queues": len(queues), "high": len(high), "normal": len(normal), "low": len(low),
            "requests_today": total, "healthy": True}
