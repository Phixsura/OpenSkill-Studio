"""App user engagement — user engagement metrics and cohort analysis."""

import html
from collections import defaultdict


def build_engagement_metrics(*, events: list[dict], period: str = "30d") -> dict:
    dau: dict[str, set] = defaultdict(set)
    wau: dict[str, set] = defaultdict(set)
    actions: dict[str, int] = defaultdict(int)
    for e in events:
        user = e.get("user_id", "")
        day = e.get("timestamp", "")[:10]
        week = e.get("timestamp", "")[:7]
        action = e.get("action", "view")
        if user:
            dau[day].add(user)
            wau[week].add(user)
        actions[action] += 1
    avg_dau = round(sum(len(u) for u in dau.values()) / max(len(dau), 1))
    avg_wau = round(sum(len(u) for u in wau.values()) / max(len(wau), 1))
    stickiness = round(avg_dau / max(avg_wau, 1) * 100, 1)
    top_actions = sorted(actions.items(), key=lambda x: -x[1])[:5]
    return {
        "period": period, "total_events": len(events),
        "avg_dau": avg_dau, "avg_wau": avg_wau,
        "stickiness_pct": stickiness,
        "top_actions": [{"action": a, "count": c} for a, c in top_actions],
    }
