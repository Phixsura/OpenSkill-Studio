"""Database connection pool — manage and monitor connection pools."""
from __future__ import annotations


def create_pool(name: str, max_size: int = 20, min_size: int = 2, idle_timeout: int = 300) -> dict:
    return {"name": name, "max_size": max_size, "min_size": min_size,
            "idle_timeout": idle_timeout, "active": 0, "idle": min_size,
            "waiting": 0, "total_acquired": 0, "total_released": 0}


def pool_status(pool: dict) -> dict:
    total_conns = pool["active"] + pool["idle"]
    utilization = round(pool["active"] / max(pool["max_size"], 1) * 100, 1)
    health = "healthy" if utilization < 70 else "busy" if utilization < 90 else "saturated"
    return {"name": pool["name"], "active": pool["active"], "idle": pool["idle"],
            "total": total_conns, "max_size": pool["max_size"],
            "utilization": utilization, "health": health,
            "waiting": pool["waiting"]}


def acquire(pool: dict) -> dict:
    if pool["idle"] > 0:
        pool["idle"] -= 1
        pool["active"] += 1
        pool["total_acquired"] += 1
        return {"acquired": True, "source": "idle"}
    if pool["active"] < pool["max_size"]:
        pool["active"] += 1
        pool["total_acquired"] += 1
        return {"acquired": True, "source": "new"}
    pool["waiting"] += 1
    return {"acquired": False, "reason": "pool_exhausted", "waiting": pool["waiting"]}


def release(pool: dict) -> dict:
    if pool["active"] <= 0:
        return {"released": False, "error": "no_active_connections"}
    pool["active"] -= 1
    pool["idle"] += 1
    pool["total_released"] += 1
    if pool["waiting"] > 0:
        pool["waiting"] -= 1
    return {"released": True, "active": pool["active"], "idle": pool["idle"]}
