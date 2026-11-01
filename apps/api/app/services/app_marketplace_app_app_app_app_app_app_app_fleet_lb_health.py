"""Fleet load balancer health — track LB backend health."""
from __future__ import annotations
def fleet_lb_health(lbs: list[dict]) -> dict:
    healthy_backends = sum(lb.get("healthy_backends", 0) for lb in lbs)
    total_backends = sum(lb.get("total_backends", 0) for lb in lbs)
    pct = round(healthy_backends / max(total_backends, 1) * 100, 1)
    return {"lbs": len(lbs), "healthy_backends": healthy_backends,
            "total_backends": total_backends, "health_pct": pct, "ok": pct >= 95}
