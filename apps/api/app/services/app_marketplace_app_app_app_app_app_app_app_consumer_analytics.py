"""API consumer analytics — analyze API consumers and their usage patterns."""
from __future__ import annotations
from collections import defaultdict


def analyze_consumers(requests: list[dict]) -> dict:
    by_consumer: dict[str, dict] = defaultdict(lambda: {"requests": 0, "errors": 0, "total_ms": 0})
    for r in requests:
        cid = r.get("consumer_id", "anonymous")
        by_consumer[cid]["requests"] += 1
        by_consumer[cid]["total_ms"] += r.get("latency_ms", 0)
        if r.get("status", 200) >= 400:
            by_consumer[cid]["errors"] += 1
    consumers = []
    for cid, data in sorted(by_consumer.items(), key=lambda x: -x[1]["requests"]):
        avg_ms = round(data["total_ms"] / max(data["requests"], 1), 1)
        err_rate = round(data["errors"] / max(data["requests"], 1) * 100, 1)
        consumers.append({"consumer_id": cid, "requests": data["requests"],
                          "avg_latency_ms": avg_ms, "error_rate_pct": err_rate})
    return {"consumers": consumers, "total_consumers": len(consumers),
            "total_requests": len(requests)}
