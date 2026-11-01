"""Connection pool — monitor and manage database connection pools."""


def get_pool_status(*, pools: list[dict]) -> dict:
    results = []
    for pool in pools:
        active = pool.get("active", 0)
        idle = pool.get("idle", 0)
        max_size = pool.get("max_size", 20)
        total = active + idle
        utilization = round(active / max(max_size, 1) * 100, 1)
        results.append({
            "name": pool["name"],
            "active": active,
            "idle": idle,
            "total": total,
            "max_size": max_size,
            "utilization_pct": utilization,
            "healthy": utilization < 90,
            "waiting": pool.get("waiting", 0),
        })
    exhausted = [r for r in results if not r["healthy"]]
    return {
        "pools": results,
        "total_pools": len(results),
        "exhausted_count": len(exhausted),
        "overall_health": "healthy" if not exhausted else "critical",
    }


def recommend_pool_size(*, avg_queries_per_sec: float, avg_query_ms: float,
                          target_utilization: float = 70) -> dict:
    concurrent = avg_queries_per_sec * (avg_query_ms / 1000)
    recommended = max(int(concurrent / (target_utilization / 100)) + 2, 5)
    return {
        "avg_concurrent_queries": round(concurrent, 1),
        "recommended_pool_size": recommended,
        "target_utilization_pct": target_utilization,
        "headroom": recommended - int(concurrent),
    }
