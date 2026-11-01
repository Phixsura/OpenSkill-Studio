"""Fleet DNS resolution — track DNS lookup performance."""
from __future__ import annotations
def fleet_dns_stats(resolvers: list[dict]) -> dict:
    avg_ms = round(sum(r.get("avg_ms", 0) for r in resolvers) / max(len(resolvers), 1), 1)
    failures = sum(r.get("failures", 0) for r in resolvers)
    return {"avg_resolve_ms": avg_ms, "total_failures": failures,
            "resolvers": len(resolvers), "healthy": avg_ms < 50 and failures == 0}
