"""Health dashboard — unified health view across all app components."""


COMPONENT_TYPES = {"api", "database", "cache", "queue", "cdn", "search", "storage"}


def build_health_dashboard(*, components: list[dict]) -> dict:
    results = []
    for comp in components:
        latency = comp.get("latency_ms", 0)
        error_rate = comp.get("error_rate", 0)
        healthy = latency < 1000 and error_rate < 5
        results.append({
            "name": comp["name"],
            "type": comp.get("type", "service"),
            "status": "healthy" if healthy else "degraded" if error_rate < 10 else "down",
            "latency_ms": latency,
            "error_rate": error_rate,
            "uptime_pct": comp.get("uptime_pct", 100),
        })
    healthy_count = sum(1 for r in results if r["status"] == "healthy")
    return {
        "components": results,
        "total": len(results),
        "healthy": healthy_count,
        "degraded": sum(1 for r in results if r["status"] == "degraded"),
        "down": sum(1 for r in results if r["status"] == "down"),
        "overall": "healthy" if healthy_count == len(results) else "degraded" if sum(1 for r in results if r["status"] == "down") == 0 else "outage",
    }
