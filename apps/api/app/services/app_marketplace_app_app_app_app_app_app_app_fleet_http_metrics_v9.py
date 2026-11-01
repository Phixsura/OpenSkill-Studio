"""Fleet HTTP Metrics v9 — track HTTP status code distribution."""
from __future__ import annotations
def fleet_http_metrics_v9(endpoints: list[dict]) -> dict:
    ok_2xx = sum(e.get("2xx", 0) for e in endpoints)
    redirect_3xx = sum(e.get("3xx", 0) for e in endpoints)
    client_4xx = sum(e.get("4xx", 0) for e in endpoints)
    server_5xx = sum(e.get("5xx", 0) for e in endpoints)
    total = ok_2xx + redirect_3xx + client_4xx + server_5xx
    return {"endpoints": len(endpoints), "2xx": ok_2xx, "3xx": redirect_3xx,
            "4xx": client_4xx, "5xx": server_5xx, "error_rate_pct": round(server_5xx / total * 100, 2) if total else 0,
            "healthy": server_5xx < total * 0.01 if total else True}
