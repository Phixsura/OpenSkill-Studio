"""Message queue monitor — track queue depths, throughput, and consumer lag."""
from __future__ import annotations


def analyze_queues(queues: list[dict]) -> dict:
    results = []
    total_depth = 0
    total_throughput = 0
    alerts = []
    for q in queues:
        name = q.get("name", "")
        depth = q.get("depth", 0)
        enqueue_rate = q.get("enqueue_rate", 0)
        dequeue_rate = q.get("dequeue_rate", 0)
        consumers = q.get("consumers", 0)
        lag = max(0, depth)
        growing = enqueue_rate > dequeue_rate
        health = "critical" if depth > 10000 or consumers == 0 else \
                 "warning" if depth > 1000 or growing else "healthy"
        total_depth += depth
        total_throughput += dequeue_rate
        if health != "healthy":
            alerts.append({"queue": name, "health": health, "depth": depth})
        results.append({"name": name, "depth": depth, "lag": lag,
                         "enqueue_rate": enqueue_rate, "dequeue_rate": dequeue_rate,
                         "consumers": consumers, "growing": growing, "health": health})
    return {"queues": results, "total_depth": total_depth,
            "total_throughput": total_throughput, "alerts": alerts,
            "overall_health": "critical" if any(a["health"] == "critical" for a in alerts) else \
                              "warning" if alerts else "healthy"}
