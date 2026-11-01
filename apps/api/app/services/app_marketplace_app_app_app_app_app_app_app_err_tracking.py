"""Error tracking dashboard — aggregate and rank errors across services."""
from __future__ import annotations


def track_errors(errors: list[dict]) -> dict:
    by_type: dict[str, dict] = {}
    for e in errors:
        etype = e.get("type", "unknown")
        if etype not in by_type:
            by_type[etype] = {"type": etype, "count": 0, "services": set(),
                               "first_seen": e.get("timestamp", 0)}
        by_type[etype]["count"] += 1
        by_type[etype]["services"].add(e.get("service", ""))
    ranked = sorted(by_type.values(), key=lambda x: -x["count"])
    for r in ranked:
        r["services"] = sorted(r["services"])
        r["service_count"] = len(r["services"])
    total = sum(r["count"] for r in ranked)
    return {"errors": ranked, "total_errors": total, "unique_types": len(ranked),
            "top_error": ranked[0]["type"] if ranked else None}


def error_trend(current_count: int, previous_count: int) -> dict:
    delta = current_count - previous_count
    pct = round(delta / max(previous_count, 1) * 100, 1)
    return {"current": current_count, "previous": previous_count,
            "delta": delta, "pct_change": pct,
            "trend": "increasing" if delta > 0 else "decreasing" if delta < 0 else "stable"}
