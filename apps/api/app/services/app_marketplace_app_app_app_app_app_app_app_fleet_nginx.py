"""Fleet NGINX — track NGINX ingress controller metrics."""
from __future__ import annotations
def fleet_nginx_status(controllers: list[dict]) -> dict:
    active_conns = sum(c.get("active_connections", 0) for c in controllers)
    requests_per_sec = sum(c.get("rps", 0) for c in controllers)
    errors_5xx = sum(c.get("errors_5xx", 0) for c in controllers)
    return {"controllers": len(controllers), "active_connections": active_conns,
            "rps": requests_per_sec, "errors_5xx": errors_5xx, "healthy": errors_5xx == 0}
