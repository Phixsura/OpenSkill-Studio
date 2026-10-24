"""Fleet tRPC — track end-to-end type-safe API health."""
from __future__ import annotations
def fleet_trpc_status(routers: list[dict]) -> dict:
    procedures = sum(r.get("procedures", 0) for r in routers)
    calls_24h = sum(r.get("calls_24h", 0) for r in routers)
    errors = sum(r.get("errors_24h", 0) for r in routers)
    return {"routers": len(routers), "procedures": procedures, "calls_24h": calls_24h,
            "errors_24h": errors, "healthy": errors == 0}
