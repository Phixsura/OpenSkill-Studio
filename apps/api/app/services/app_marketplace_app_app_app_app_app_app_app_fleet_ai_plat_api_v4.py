"""Fleet AI API v4 — track ultimate AI platform API management."""
from __future__ import annotations
def fleet_ai_api_v4(gateways: list[dict]) -> dict:
    active = [g for g in gateways if g.get("active", True)]
    endpoints = sum(g.get("endpoints", 0) for g in gateways)
    requests_24h = sum(g.get("requests_24h", 0) for g in gateways)
    p99_ms = round(sum(g.get("p99_ms", 0) for g in gateways) / max(len(gateways), 1), 1)
    error_rate = round(sum(g.get("error_pct", 0) for g in gateways) / max(len(gateways), 1), 2)
    return {"gateways": len(gateways), "active": len(active), "endpoints": endpoints,
            "requests_24h": requests_24h, "p99_ms": p99_ms, "error_rate": error_rate, "healthy": error_rate < 0.1}
