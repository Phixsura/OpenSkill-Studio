"""Connection pool — manage database/HTTP connection pools for apps."""


def create_pool_config(*, app_id: str, pool_type: str, min_size: int = 2,
                         max_size: int = 10, idle_timeout_seconds: int = 300) -> dict:
    valid_types = {"database", "http", "redis"}
    if pool_type not in valid_types:
        return {"error": f"Invalid pool type. Use: {', '.join(sorted(valid_types))}"}
    if min_size > max_size:
        return {"error": "min_size cannot exceed max_size"}
    return {"app_id": app_id, "pool_type": pool_type, "min_size": min_size,
            "max_size": max_size, "idle_timeout_seconds": idle_timeout_seconds, "error": None}


def get_pool_health(*, active: int, idle: int, max_size: int, waiting: int) -> dict:
    utilization = round((active + idle) / max(max_size, 1) * 100, 1)
    healthy = waiting == 0 and utilization < 90
    return {"active": active, "idle": idle, "waiting": waiting,
            "utilization_pct": utilization, "healthy": healthy,
            "recommendation": "Consider increasing pool size" if utilization > 80 else None}


def compute_pool_metrics(*, samples: list[dict]) -> dict:
    if not samples:
        return {"avg_active": 0, "avg_wait_ms": 0, "peak_active": 0}
    return {
        "avg_active": round(sum(s.get("active", 0) for s in samples) / len(samples), 1),
        "avg_wait_ms": round(sum(s.get("wait_ms", 0) for s in samples) / len(samples), 1),
        "peak_active": max(s.get("active", 0) for s in samples),
    }
