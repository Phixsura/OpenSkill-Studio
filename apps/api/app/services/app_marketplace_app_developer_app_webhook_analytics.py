"""Webhook analytics — deep analytics on webhook delivery performance."""

from collections import defaultdict


def compute_delivery_metrics(*, deliveries: list[dict]) -> dict:
    if not deliveries:
        return {"total": 0, "success_rate": 0, "avg_latency_ms": 0, "p99_ms": 0}
    successes = sum(1 for d in deliveries if d.get("success"))
    latencies = sorted(d.get("latency_ms", 0) for d in deliveries)
    p99_idx = max(0, int(len(latencies) * 0.99) - 1)
    return {
        "total": len(deliveries), "success_rate": round(successes / len(deliveries) * 100, 1),
        "avg_latency_ms": round(sum(latencies) / len(latencies)),
        "p99_ms": latencies[p99_idx], "failures": len(deliveries) - successes,
    }


def group_by_event_type(*, deliveries: list[dict]) -> dict:
    groups = defaultdict(lambda: {"count": 0, "successes": 0, "total_ms": 0})
    for d in deliveries:
        et = d.get("event_type", "unknown")
        groups[et]["count"] += 1
        if d.get("success"):
            groups[et]["successes"] += 1
        groups[et]["total_ms"] += d.get("latency_ms", 0)
    result = []
    for et, data in sorted(groups.items(), key=lambda x: -x[1]["count"]):
        result.append({"event_type": et, "count": data["count"],
                        "success_rate": round(data["successes"] / data["count"] * 100, 1),
                        "avg_ms": round(data["total_ms"] / data["count"])})
    return {"event_types": result, "unique_types": len(result)}


def identify_failing_endpoints(*, deliveries: list[dict], threshold: float = 50) -> list[dict]:
    by_url = defaultdict(lambda: {"total": 0, "failures": 0})
    for d in deliveries:
        url = d.get("url", "")
        by_url[url]["total"] += 1
        if not d.get("success"):
            by_url[url]["failures"] += 1
    failing = []
    for url, data in by_url.items():
        fail_rate = data["failures"] / data["total"] * 100
        if fail_rate >= threshold:
            failing.append({"url": url, "failure_rate": round(fail_rate, 1), "total": data["total"]})
    return sorted(failing, key=lambda x: -x["failure_rate"])
