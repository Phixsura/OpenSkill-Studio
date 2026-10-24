"""Usage analytics — app usage metrics with funnel analysis."""

import html
from collections import defaultdict


def build_usage_summary(*, events: list[dict], period: str = "7d") -> dict:
    by_action: dict[str, int] = defaultdict(int)
    unique_users: set[str] = set()
    for e in events:
        by_action[e.get("action", "unknown")] += 1
        uid = e.get("user_id")
        if uid:
            unique_users.add(uid)
    top_actions = sorted(by_action.items(), key=lambda x: -x[1])[:10]
    return {"period": period, "total_events": len(events),
            "unique_users": len(unique_users),
            "top_actions": [{"action": a, "count": c} for a, c in top_actions],
            "events_per_user": round(len(events) / max(len(unique_users), 1), 1)}


def build_funnel(*, steps: list[dict]) -> dict:
    items = []
    prev_count = None
    for s in steps:
        count = s.get("count", 0)
        drop_off = round((1 - count / prev_count) * 100, 1) if prev_count and prev_count > 0 else 0
        conv = round(count / steps[0]["count"] * 100, 1) if steps[0]["count"] > 0 else 0
        items.append({"step": html.escape(s.get("name", "")), "count": count,
                       "drop_off_pct": drop_off, "conversion_pct": conv})
        prev_count = count
    overall = items[-1]["conversion_pct"] if items else 0
    return {"steps": items, "total_steps": len(items), "overall_conversion_pct": overall}
