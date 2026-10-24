"""Worker pool manager — manage background worker pools."""
from __future__ import annotations


def create_pool(name: str, size: int, queue_depth: int = 0) -> dict:
    return {"name": name, "size": size, "active": 0, "idle": size,
            "queue_depth": queue_depth, "processed": 0, "failed": 0}


def process_job(pool: dict, success: bool = True) -> dict:
    if pool["idle"] <= 0 and pool["active"] >= pool["size"]:
        pool["queue_depth"] += 1
        return {"processed": False, "queued": True, "queue_depth": pool["queue_depth"]}
    if pool["idle"] > 0:
        pool["idle"] -= 1
    pool["active"] += 1
    pool["processed"] += 1
    if not success:
        pool["failed"] += 1
    pool["active"] -= 1
    pool["idle"] += 1
    return {"processed": True, "success": success, "total_processed": pool["processed"]}


def pool_health(pool: dict) -> dict:
    utilization = round(pool["active"] / max(pool["size"], 1) * 100)
    failure_rate = round(pool["failed"] / max(pool["processed"], 1) * 100, 1)
    backlog = pool["queue_depth"] > pool["size"]
    return {"name": pool["name"], "utilization": utilization,
            "failure_rate": failure_rate, "backlog": backlog,
            "healthy": not backlog and failure_rate < 5}
