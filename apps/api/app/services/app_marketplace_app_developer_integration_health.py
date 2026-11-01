"""Integration health — monitor health of all connected integrations."""


def check_integration_health(*, integrations: list[dict]) -> dict:
    results = []
    for intg in integrations:
        status = "healthy" if intg.get("last_ping_ms", 9999) < 5000 and intg.get("error_count", 0) < 3 else "degraded" if intg.get("error_count", 0) < 10 else "down"
        results.append({"name": intg["name"], "status": status,
                         "last_ping_ms": intg.get("last_ping_ms", 0),
                         "error_count": intg.get("error_count", 0)})
    healthy = sum(1 for r in results if r["status"] == "healthy")
    return {"integrations": results, "total": len(results), "healthy": healthy,
            "overall": "healthy" if healthy == len(results) else "degraded" if healthy > 0 else "down"}
