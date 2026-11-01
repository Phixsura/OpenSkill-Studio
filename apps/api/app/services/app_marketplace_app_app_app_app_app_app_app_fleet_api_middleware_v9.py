"""Fleet API Middleware v9 — track API middleware chain execution."""
from __future__ import annotations
def fleet_api_middleware_v9(middlewares: list[dict]) -> dict:
    active = [m for m in middlewares if m.get("active")]
    auth_mw = [m for m in middlewares if m.get("type") == "auth"]
    logging_mw = [m for m in middlewares if m.get("type") == "logging"]
    avg_overhead = sum(m.get("overhead_ms", 0) for m in middlewares) / len(middlewares) if middlewares else 0
    return {"middlewares": len(middlewares), "active": len(active), "auth": len(auth_mw),
            "logging": len(logging_mw), "avg_overhead_ms": round(avg_overhead, 2), "healthy": avg_overhead < 5}
