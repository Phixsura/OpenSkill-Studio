"""Error tracking — group, deduplicate, and prioritize runtime errors."""

import hashlib


def fingerprint_error(*, message: str, stack_trace: str) -> str:
    normalized = stack_trace.strip().split("\n")[0] if stack_trace else message
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def group_errors(*, errors: list[dict]) -> dict:
    groups: dict[str, dict] = {}
    for err in errors:
        fp = fingerprint_error(message=err.get("message", ""), stack_trace=err.get("stack_trace", ""))
        if fp not in groups:
            groups[fp] = {"fingerprint": fp, "message": err.get("message", ""),
                          "count": 0, "users_affected": set(), "first_seen": err.get("timestamp"),
                          "last_seen": err.get("timestamp"), "level": err.get("level", "error")}
        groups[fp]["count"] += 1
        groups[fp]["users_affected"].add(err.get("user_id", "anon"))
        groups[fp]["last_seen"] = err.get("timestamp")
    result = []
    for g in sorted(groups.values(), key=lambda x: x["count"], reverse=True):
        result.append({**g, "users_affected": len(g["users_affected"])})
    return {"groups": result, "unique_errors": len(result),
            "total_occurrences": sum(g["count"] for g in result)}


def get_error_trend(*, error_counts: list[int]) -> dict:
    if len(error_counts) < 2:
        return {"trend": "stable", "change_pct": 0}
    recent = sum(error_counts[-3:]) / min(len(error_counts), 3)
    older = sum(error_counts[:-3]) / max(len(error_counts) - 3, 1)
    change = round((recent - older) / max(older, 0.01) * 100, 1)
    trend = "increasing" if change > 20 else "decreasing" if change < -20 else "stable"
    return {"trend": trend, "change_pct": change}
