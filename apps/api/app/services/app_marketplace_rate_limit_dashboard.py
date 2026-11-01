"""Rate limit dashboard — visualize rate limit usage across all endpoints."""

from collections import defaultdict


def compute_rate_limit_usage(*, endpoints: list[dict]) -> dict:
    total_capacity = sum(e.get("limit", 0) for e in endpoints)
    total_used = sum(e.get("current", 0) for e in endpoints)
    hotspots = [e for e in endpoints if e.get("current", 0) / max(e.get("limit", 1), 1) >=  0.8]
    return {"total_capacity": total_capacity, "total_used": total_used,
            "usage_pct": round(total_used / max(total_capacity, 1) * 100, 1),
            "hotspot_count": len(hotspots), "endpoint_count": len(endpoints)}


def get_rate_limited_requests(*, requests: list[dict]) -> dict:
    limited = [r for r in requests if r.get("status_code") == 429]
    by_endpoint = defaultdict(int)
    for r in limited:
        by_endpoint[r.get("path", "")] += 1
    return {"total_limited": len(limited), "total_requests": len(requests),
            "rate": round(len(limited) / max(len(requests), 1) * 100, 2),
            "by_endpoint": dict(sorted(by_endpoint.items(), key=lambda x: -x[1]))}


def suggest_limit_adjustments(*, usage: dict, hotspots: list[dict]) -> list[dict]:
    suggestions = []
    for h in hotspots:
        pct = h.get("current", 0) / max(h.get("limit", 1), 1) * 100
        if pct > 95:
            suggestions.append({"endpoint": h.get("path"), "current_limit": h.get("limit"),
                                 "suggested_limit": h.get("limit", 100) * 2, "reason": "Consistently at capacity"})
        elif pct > 80:
            suggestions.append({"endpoint": h.get("path"), "current_limit": h.get("limit"),
                                 "suggested_limit": int(h.get("limit", 100) * 1.5), "reason": "Approaching limit"})
    return suggestions
