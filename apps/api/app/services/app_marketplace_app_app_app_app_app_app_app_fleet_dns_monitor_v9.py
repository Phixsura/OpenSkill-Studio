"""Fleet DNS Monitor v9 — track DNS resolution latency and failures."""
from __future__ import annotations
def fleet_dns_monitor_v9(domains: list[dict]) -> dict:
    resolving = [d for d in domains if d.get("resolving", True)]
    avg_ttl = sum(d.get("ttl_sec", 0) for d in domains) / len(domains) if domains else 0
    failures = sum(d.get("failures_today", 0) for d in domains)
    return {"domains": len(domains), "resolving": len(resolving), "avg_ttl_sec": round(avg_ttl, 1),
            "failures_today": failures, "healthy": failures == 0}
