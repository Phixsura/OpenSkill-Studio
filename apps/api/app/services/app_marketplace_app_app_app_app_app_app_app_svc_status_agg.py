"""Service status aggregator — aggregate status from multiple sources."""
from __future__ import annotations
from collections import defaultdict


def aggregate_status(reports: list[dict]) -> dict:
    by_service: dict[str, list[str]] = defaultdict(list)
    for r in reports:
        by_service[r["service"]].append(r.get("status", "unknown"))
    results = []
    for svc, statuses in sorted(by_service.items()):
        if all(s == "healthy" for s in statuses):
            consensus = "healthy"
        elif any(s == "down" for s in statuses):
            consensus = "down"
        else:
            consensus = "degraded"
        results.append({"service": svc, "consensus": consensus,
                        "reports": len(statuses), "sources": statuses})
    healthy = sum(1 for r in results if r["consensus"] == "healthy")
    return {"services": results, "total": len(results),
            "healthy": healthy, "unhealthy": len(results) - healthy}
