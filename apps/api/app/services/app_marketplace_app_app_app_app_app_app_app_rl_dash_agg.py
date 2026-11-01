"""Rate limit dashboard aggregator — aggregate rate limit stats across services."""
from __future__ import annotations
from collections import defaultdict


def aggregate_rate_limits(events: list[dict]) -> dict:
    by_key: dict[str, dict] = defaultdict(lambda: {"allowed": 0, "denied": 0})
    for e in events:
        key = e.get("key", "unknown")
        if e.get("allowed"):
            by_key[key]["allowed"] += 1
        else:
            by_key[key]["denied"] += 1
    results = []
    for key, data in sorted(by_key.items(), key=lambda x: -x[1]["denied"]):
        total = data["allowed"] + data["denied"]
        deny_rate = round(data["denied"] / max(total, 1) * 100, 1)
        results.append({"key": key, **data, "total": total, "deny_rate": deny_rate})
    total_denied = sum(d["denied"] for d in by_key.values())
    return {"keys": results, "total_events": len(events),
            "total_denied": total_denied, "unique_keys": len(by_key)}
