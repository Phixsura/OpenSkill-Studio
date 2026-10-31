"""Mesh retry analytics — analyze retry patterns across the service mesh."""
from __future__ import annotations
from collections import defaultdict


def analyze_retries(events: list[dict]) -> dict:
    by_pair: dict[str, dict] = defaultdict(lambda: {"total": 0, "retries": 0, "successes_after_retry": 0})
    for e in events:
        key = f"{e['source']}→{e['destination']}"
        by_pair[key]["total"] += 1
        if e.get("is_retry"):
            by_pair[key]["retries"] += 1
            if e.get("status", 500) < 400:
                by_pair[key]["successes_after_retry"] += 1
    pairs = []
    for key, data in sorted(by_pair.items(), key=lambda x: -x[1]["retries"]):
        retry_rate = round(data["retries"] / max(data["total"], 1) * 100, 1)
        success_rate = round(data["successes_after_retry"] / max(data["retries"], 1) * 100, 1)
        pairs.append({"pair": key, "total": data["total"], "retries": data["retries"],
                       "retry_rate": retry_rate, "retry_success_rate": success_rate})
    total_retries = sum(p["retries"] for p in pairs)
    return {"pairs": pairs, "total_requests": len(events),
            "total_retries": total_retries, "pairs_with_retries": sum(1 for p in pairs if p["retries"] > 0)}
