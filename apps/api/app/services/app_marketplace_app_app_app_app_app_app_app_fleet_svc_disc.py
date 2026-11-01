"""Fleet service discovery — track DNS-based service discovery health."""
from __future__ import annotations
def fleet_svc_discovery(services: list[dict]) -> dict:
    resolvable = [s for s in services if s.get("dns_resolvable", True)]
    stale_dns = [s for s in services if s.get("dns_stale", False)]
    return {"total": len(services), "resolvable": len(resolvable),
            "stale_dns": len(stale_dns), "healthy": len(resolvable) == len(services) and len(stale_dns) == 0}
