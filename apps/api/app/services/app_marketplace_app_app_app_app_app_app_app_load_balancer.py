"""Load balancer config — manage backend pools and health."""
from __future__ import annotations


ALGORITHMS = {"round_robin", "least_connections", "ip_hash", "random", "weighted"}


def create_pool(name: str, algorithm: str, backends: list[dict]) -> dict:
    if algorithm not in ALGORITHMS:
        return {"created": False, "error": f"unknown algorithm, use {sorted(ALGORITHMS)}"}
    total_weight = sum(b.get("weight", 1) for b in backends)
    pool_backends = []
    for b in backends:
        w = round(b.get("weight", 1) / total_weight * 100, 1)
        pool_backends.append({"address": b["address"], "weight": w,
                              "healthy": b.get("healthy", True)})
    healthy = sum(1 for b in pool_backends if b["healthy"])
    return {"created": True, "name": name, "algorithm": algorithm,
            "backends": pool_backends, "total": len(pool_backends),
            "healthy": healthy, "capacity_pct": round(healthy / max(len(pool_backends), 1) * 100)}


def select_backend(pool: dict, request_num: int = 0) -> dict:
    healthy_backends = [b for b in pool["backends"] if b["healthy"]]
    if not healthy_backends:
        return {"selected": False, "error": "no_healthy_backends"}
    if pool["algorithm"] == "round_robin":
        idx = request_num % len(healthy_backends)
    else:
        idx = 0
    return {"selected": True, "backend": healthy_backends[idx]["address"]}
