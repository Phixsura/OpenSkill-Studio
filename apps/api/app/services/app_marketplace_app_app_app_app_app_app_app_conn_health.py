"""Connection health checker — verify connectivity to external dependencies."""
from __future__ import annotations


def check_connections(connections: list[dict]) -> dict:
    results = []
    for conn in connections:
        healthy = conn.get("latency_ms", 0) < conn.get("timeout_ms", 5000) and conn.get("reachable", True)
        results.append({"name": conn["name"], "type": conn.get("type", "tcp"),
                        "healthy": healthy, "latency_ms": conn.get("latency_ms", 0),
                        "error": conn.get("error", "") if not healthy else ""})
    healthy_count = sum(1 for r in results if r["healthy"])
    return {"connections": results, "total": len(results), "healthy": healthy_count,
            "all_healthy": healthy_count == len(results)}


def connection_summary(checks: list[dict]) -> dict:
    by_type: dict[str, dict] = {}
    for c in checks:
        t = c.get("type", "unknown")
        if t not in by_type:
            by_type[t] = {"healthy": 0, "total": 0}
        by_type[t]["total"] += 1
        if c.get("healthy"):
            by_type[t]["healthy"] += 1
    return {"by_type": by_type}
