"""Smart routing — intelligent request routing based on latency, load, and health."""


def select_best_instance(*, instances: list[dict], strategy: str = "least_latency") -> dict | None:
    healthy = [i for i in instances if i.get("health") == "healthy"]
    if not healthy:
        return None
    if strategy == "least_latency":
        return min(healthy, key=lambda i: i.get("avg_latency_ms", 9999))
    elif strategy == "least_connections":
        return min(healthy, key=lambda i: i.get("active_connections", 9999))
    elif strategy == "weighted":
        total_weight = sum(i.get("weight", 1) for i in healthy)
        import hashlib, time
        h = int(hashlib.md5(str(time.time()).encode()).hexdigest(), 16) % total_weight
        cumulative = 0
        for inst in healthy:
            cumulative += inst.get("weight", 1)
            if h < cumulative:
                return inst
    return healthy[0]


def compute_routing_stats(*, decisions: list[dict]) -> dict:
    by_instance = {}
    for d in decisions:
        iid = d.get("instance_id", "unknown")
        by_instance.setdefault(iid, {"count": 0, "total_ms": 0})
        by_instance[iid]["count"] += 1
        by_instance[iid]["total_ms"] += d.get("latency_ms", 0)
    result = []
    for iid, data in by_instance.items():
        result.append({"instance_id": iid, "requests": data["count"],
                        "avg_ms": round(data["total_ms"] / data["count"])})
    return {"instances": sorted(result, key=lambda x: -x["requests"]), "total_decisions": len(decisions)}


def detect_hot_instance(*, stats: dict, threshold_pct: float = 60) -> dict | None:
    total = stats.get("total_decisions", 0)
    for inst in stats.get("instances", []):
        pct = inst["requests"] / max(total, 1) * 100
        if pct > threshold_pct:
            return {"instance_id": inst["instance_id"], "pct": round(pct, 1),
                    "recommendation": "Rebalance traffic — instance overloaded"}
    return None
