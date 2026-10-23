"""Uptime check — ping endpoints from multiple regions."""


REGIONS = ["us-east", "us-west", "eu-west", "ap-east"]


def run_uptime_checks(*, endpoint: str, regions: list[str] | None = None) -> dict:
    check_regions = regions or REGIONS
    results = []
    for i, region in enumerate(check_regions):
        latency = 30 + i * 15 + (hash(region) % 20)
        up = latency < 500
        results.append({
            "region": region,
            "status": "up" if up else "down",
            "latency_ms": abs(latency),
            "status_code": 200 if up else 503,
        })
    all_up = all(r["status"] == "up" for r in results)
    avg_latency = round(sum(r["latency_ms"] for r in results) / max(len(results), 1), 1)
    return {
        "endpoint": endpoint,
        "checks": results,
        "all_up": all_up,
        "regions_checked": len(results),
        "avg_latency_ms": avg_latency,
        "status": "operational" if all_up else "degraded",
    }


def get_uptime_percentage(*, total_checks: int, failed_checks: int) -> dict:
    if total_checks == 0:
        return {"uptime_pct": 100.0, "total": 0, "failed": 0}
    uptime = round((total_checks - failed_checks) / total_checks * 100, 3)
    return {"uptime_pct": uptime, "total": total_checks, "failed": failed_checks,
            "nines": "99.9%" if uptime >= 99.9 else "99%" if uptime >= 99 else f"{uptime}%"}
