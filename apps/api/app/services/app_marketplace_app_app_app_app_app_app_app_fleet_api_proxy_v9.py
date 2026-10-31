"""Fleet API Proxy v9 — track reverse proxy routing and health."""
from __future__ import annotations
def fleet_api_proxy_v9(proxies: list[dict]) -> dict:
    active = [p for p in proxies if p.get("active")]
    rps = sum(p.get("rps", 0) for p in proxies)
    backends = sum(p.get("backends", 0) for p in proxies)
    errors = sum(p.get("errors_today", 0) for p in proxies)
    return {"proxies": len(proxies), "active": len(active), "total_rps": rps,
            "backends": backends, "errors": errors, "healthy": errors == 0}
