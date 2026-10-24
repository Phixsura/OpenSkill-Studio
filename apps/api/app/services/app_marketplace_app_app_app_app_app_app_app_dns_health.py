"""DNS health monitor — check DNS resolution health for services."""
from __future__ import annotations


def check_dns_health(records: list[dict]) -> dict:
    healthy = []
    unhealthy = []
    for r in records:
        resolved = r.get("resolved", False)
        ttl = r.get("ttl", 0)
        entry = {"domain": r["domain"], "type": r.get("type", "A"),
                 "resolved": resolved, "ttl": ttl,
                 "ip": r.get("ip", ""), "latency_ms": r.get("latency_ms", 0)}
        if resolved and ttl > 0:
            healthy.append(entry)
        else:
            unhealthy.append(entry)
    return {"healthy": len(healthy), "unhealthy": len(unhealthy),
            "total": len(records), "all_healthy": len(unhealthy) == 0,
            "records": healthy + unhealthy}


def detect_stale_records(records: list[dict], max_ttl: int = 86400) -> list[dict]:
    stale = []
    for r in records:
        if r.get("ttl", 0) > max_ttl:
            stale.append({"domain": r["domain"], "ttl": r["ttl"],
                          "exceeds_by": r["ttl"] - max_ttl})
    return sorted(stale, key=lambda x: -x["ttl"])
