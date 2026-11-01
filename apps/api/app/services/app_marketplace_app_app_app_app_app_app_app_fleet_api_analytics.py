"""Fleet API analytics — comprehensive API usage analytics."""
from __future__ import annotations
def fleet_api_analytics(window: dict) -> dict:
    total_calls = window.get("total_calls", 0)
    unique_consumers = window.get("unique_consumers", 0)
    avg_calls_per_consumer = round(total_calls / max(unique_consumers, 1), 1)
    top_endpoint = window.get("top_endpoint", "unknown")
    return {"total_calls": total_calls, "unique_consumers": unique_consumers,
            "avg_calls_per_consumer": avg_calls_per_consumer, "top_endpoint": top_endpoint}
